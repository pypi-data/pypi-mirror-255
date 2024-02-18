from __future__ import annotations

import random
from numbers import Number
from typing import Union, Callable, Dict
from abc import ABC, abstractmethod

from nmmo.systems import skill, item
from nmmo.lib import material
from nmmo.lib.log import EventCode
from nmmo.core.config import Config

class InvalidConstraint(Exception):
  pass

class Constraint(ABC):
  """ To check the validity of predicates
  and assist generating new predicates. Similar to gym spaces.
  """
  def __init__(self, systems=None):
    if systems is None:
      systems = []
    self._systems = systems

  # pylint: disable=unused-argument
  def check(self, config: Config, value):
    """ Checks value is in bounds given config
    """
    for system in self._systems:
      try:
        if not getattr(config,system):
          return False
      except AttributeError:
        return False
    return True

  @abstractmethod
  def sample(self, config: Config):
    """ Generator to sample valid values given config
    """
    raise NotImplementedError

  def __str__(self):
    return self.__class__.__name__

# This is a dummy function for GroupConstraint
# NOTE: config does not have team info
def sample_one_big_team(config):
  from nmmo.task.group import Group
  team = list(range(1, config.PLAYER_N+1))
  return [Group(team, 'All')]

class GroupConstraint(Constraint):
  """ Ensures that all agents of a group exist in a config
  """
  def __init__(self,
               sample_fn = sample_one_big_team,
               systems = None):
    """
    Params
      sample_fn: given a Config, return groups to select from
      systems: systems required to operate
    """
    super().__init__(systems)
    self._sample_fn = sample_fn

  def check(self, config, value):
    if not super().check(config,value):
      return False
    for agent in value.agents:
      if agent > config.PLAYER_N:
        return False
    return True

  def sample(self, config):
    return random.choice(self._sample_fn(config))

  def sample_from_teams(self, teams: Dict[int, Dict]):
    from nmmo.task.group import Group
    team_id = random.choice(list(teams.keys()))
    return Group(teams[team_id], str(team_id))

class AgentListConstraint(Constraint):
  """ Ensures that all agents of the list exist in a config
  """
  def check(self, config, value):
    for agent in value:
      if agent > config.PLAYER_N:
        return False
    return True

  def sample(self, config):
    return None

class ScalarConstraint(Constraint):
  def __init__(self,
               low:  Union[Callable, Number] = 0,
               high: Union[Callable, Number] = 1024,
               dtype = int,
               systems = None):
    super().__init__(systems)
    self._low = low
    self._high = high
    if isinstance(low, Number):
      self._low  = lambda _ : low
    if isinstance(high, Number):
      self._high = lambda _ : high
    self._dtype = dtype

  def check(self, config, value):
    if not super().check(config,value):
      return False
    if self._low(config) <= value < self._high(config):
      return True
    return False

  def sample(self, config):
    l, h = self._low(config), self._high(config)
    return self._dtype(random.random()*(h-l)+l)

class DiscreteConstraint(Constraint):
  def __init__(self, space, systems=None):
    super().__init__(systems)
    self._space = set(space)

  def check(self, config: Config, value):
    if not super().check(config,value):
      return False
    return value in self._space

  def sample(self, config: Config):
    # NOTE: this does NOT need to be deterministic
    return random.choice(self._space)

# Group Constraints
TEAM_GROUPS = GroupConstraint()
INDIVIDUAL_GROUPS=GroupConstraint()
AGENT_LIST_CONSTRAINT = AgentListConstraint()

# Tile Constraints
MATERIAL_CONSTRAINT = DiscreteConstraint(space=list(material.All.materials),
                                         systems=['TERRAIN_SYSTEM_ENABLED',
                                                  'RESOURCE_SYSTEM_ENABLED'])
HABITABLE_CONSTRAINT = DiscreteConstraint(space=list(material.Habitable.materials),
                                         systems=['TERRAIN_SYSTEM_ENABLED'])

# Event Constraints
event_names = [k for k, v in EventCode.__dict__.items() if isinstance(v,int)]
EVENTCODE_CONSTRAINT = DiscreteConstraint(space=event_names)

# Skill Constraints
combat_skills = [skill.Melee, skill.Mage, skill.Range]
harvest_skills = [skill.Fishing, skill.Herbalism, skill.Prospecting, skill.Alchemy, skill.Carving]
SKILL_CONSTRAINT = DiscreteConstraint(space=combat_skills+harvest_skills,
                                      systems=['PROFESSION_SYSTEM_ENABLED'])
COMBAT_SKILL_CONSTRAINT = DiscreteConstraint(space=combat_skills,
                                      systems=['PROFESSION_SYSTEM_ENABLED'])

# Item Constraints
armour = [item.Hat, item.Top, item.Bottom]
weapons = [item.Spear, item.Bow, item.Wand]
tools = [item.Axe, item.Gloves, item.Rod, item.Pickaxe, item.Chisel]
ammunition = [item.Runes, item.Arrow, item.Whetstone]
consumables = [item.Potion, item.Ration]
ITEM_CONSTRAINT = DiscreteConstraint(space=armour+weapons+tools+ammunition+consumables,
                                     systems=['ITEM_SYSTEM_ENABLED'])
EQUIPABLE_CONSTRAINT = DiscreteConstraint(space=armour+weapons+tools+ammunition,
                                     systems=['ITEM_SYSTEM_ENABLED'])
CONSUMABLE_CONSTRAINT = DiscreteConstraint(space=consumables,
                                           systems=['ITEM_SYSTEM_ENABLED'])
HARVEST_CONSTRAINT = DiscreteConstraint(space=weapons+ammunition+consumables,
                                        systems=['ITEM_SYSTEM_ENABLED'])

# Config Constraints
COORDINATE_CONSTRAINT = ScalarConstraint(high = lambda c: c.MAP_CENTER)
PROGRESSION_CONSTRAINT = ScalarConstraint(high = lambda c: c.PROGRESSION_LEVEL_MAX+1)
INVENTORY_CONSTRAINT = ScalarConstraint(high=lambda c: c.ITEM_INVENTORY_CAPACITY+1)
AGENT_NUMBER_CONSTRAINT = ScalarConstraint(low = 1, high = lambda c: c.PLAYER_N+1)

# Arbitrary Constraints
EVENT_NUMBER_CONSTRAINT = ScalarConstraint(low = 1, high = 110)
GOLD_CONSTRAINT = ScalarConstraint(low = 1, high = 1000)
AGENT_TYPE_CONSTRAINT = DiscreteConstraint(space=['npc','player'])
