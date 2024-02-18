from nmmo.systems.skill import Skills
from nmmo.entity import entity
from nmmo.lib.log import EventCode

# pylint: disable=no-member
class Player(entity.Entity):
  def __init__(self, realm, pos, agent, resilient=False):
    super().__init__(realm, pos, agent.iden, agent.policy)

    self.agent    = agent
    self.immortal = realm.config.IMMORTAL
    self.resources.resilient = resilient

    # Scripted hooks
    self.target = None
    self.vision = 7

    # Logs
    self.buys                     = 0
    self.sells                    = 0
    self.ration_consumed          = 0
    self.poultice_consumed        = 0
    self.ration_level_consumed    = 0
    self.poultice_level_consumed  = 0

    # initialize skills with the base level
    self.skills = Skills(realm, self)
    if realm.config.PROGRESSION_SYSTEM_ENABLED:
      for skill in self.skills.skills:
        skill.level.update(realm.config.PROGRESSION_BASE_LEVEL)

    # Gold: initialize with 1 gold (EXCHANGE_BASE_GOLD).
    # If the base amount is more than 1, alss check the npc's init gold.
    if realm.config.EXCHANGE_SYSTEM_ENABLED:
      self.gold.update(realm.config.EXCHANGE_BASE_GOLD)

  @property
  def serial(self):
    return self.ent_id

  @property
  def is_player(self) -> bool:
    return True

  @property
  def level(self) -> int:
    # a player's level is the max of all skills
    # CHECK ME: the initial level is 1 because of Basic skills,
    #   which are harvesting food/water and don't progress
    return max(e.level.val for e in self.skills.skills)

  def apply_damage(self, dmg, style):
    super().apply_damage(dmg, style)
    self.skills.apply_damage(style)

  # TODO(daveey): The returns for this function are a mess
  def receive_damage(self, source, dmg):
    if self.immortal:
      return False

    # super().receive_damage returns True if self is alive after taking dmg
    if super().receive_damage(source, dmg):
      return True

    if not self.config.ITEM_SYSTEM_ENABLED:
      return False

    # starting from here, source receive gold & inventory items
    if self.config.EXCHANGE_SYSTEM_ENABLED and source is not None:
      if self.gold.val > 0:
        source.gold.increment(self.gold.val)
        self.realm.event_log.record(EventCode.EARN_GOLD, source, amount=self.gold.val)
        self.gold.update(0)

    # TODO: make source receive the highest-level items first
    #   because source cannot take it if the inventory is full
    item_list = list(self.inventory.items)
    self._np_random.shuffle(item_list)
    for item in item_list:
      self.inventory.remove(item)

      # if source is None or NPC, destroy the item
      if source.is_player:
        # inventory.receive() returns True if the item is received
        # if source doesn't have space, inventory.receive() destroys the item
        if source.inventory.receive(item):
          self.realm.event_log.record(EventCode.LOOT_ITEM, source, item=item)
      else:
        item.destroy()

    # CHECK ME: this is an empty function. do we still need this?
    self.skills.receive_damage(dmg)
    return False

  @property
  def equipment(self):
    return self.inventory.equipment

  def packet(self):
    data = super().packet()
    data['entID']     = self.ent_id
    data['resource']  = self.resources.packet()
    data['skills']    = self.skills.packet()
    data['inventory'] = self.inventory.packet()

    return data

  def update(self, realm, actions):
    '''Post-action update. Do not include history'''
    super().update(realm, actions)

    # Spawsn battle royale style death fog
    # Starts at 0 damage on the specified config tick
    # Moves in from the edges by 1 damage per tile per tick
    # So after 10 ticks, you take 10 damage at the edge and 1 damage
    # 10 tiles in, 0 damage in farther
    # This means all agents will be force killed around
    # MAP_CENTER / 2 + 100 ticks after spawning
    fog = self.config.PLAYER_DEATH_FOG
    if fog is not None and self.realm.tick >= fog:
      row, col = self.pos
      cent = self.config.MAP_BORDER + self.config.MAP_CENTER // 2

      # Distance from center of the map
      dist = max(abs(row - cent), abs(col - cent))

      # Safe final area
      if dist > self.config.PLAYER_DEATH_FOG_FINAL_SIZE:
        # Damage based on time and distance from center
        time_dmg = self.config.PLAYER_DEATH_FOG_SPEED * (self.realm.tick - fog + 1)
        dist_dmg = dist - self.config.MAP_CENTER // 2
        dmg = max(0, dist_dmg + time_dmg)
        self.receive_damage(None, dmg)

    if not self.alive:
      return

    self.resources.update()
    self.skills.update()
