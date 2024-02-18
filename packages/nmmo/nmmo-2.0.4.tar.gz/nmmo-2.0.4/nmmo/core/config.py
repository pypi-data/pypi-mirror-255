# pylint: disable=invalid-name
from __future__ import annotations

import os
import sys
import logging

import nmmo
from nmmo.core.agent import Agent
from nmmo.core.terrain import MapGenerator
from nmmo.lib import utils, material, spawn

class Template(metaclass=utils.StaticIterable):
  def __init__(self):
    self.data = {}
    cls       = type(self)

    #Set defaults from static properties
    for k, v in cls:
      self.set(k, v)

  def override(self, **kwargs):
    for k, v in kwargs.items():
      err = f'CLI argument: {k} is not a Config property'
      assert hasattr(self, k), err
      self.set(k, v)

  def set(self, k, v):
    if not isinstance(v, property):
      try:
        setattr(self, k, v)
      except AttributeError:
        logging.error('Cannot set attribute: %s to %s', str(k), str(v))
        sys.exit()
    self.data[k] = v

  # pylint: disable=bad-builtin
  def print(self):
    key_len = 0
    for k in self.data:
      key_len = max(key_len, len(k))

    print('Configuration')
    for k, v in self.data.items():
      print(f'   {k:{key_len}s}: {v}')

  def items(self):
    return self.data.items()

  def __iter__(self):
    for k in self.data:
      yield k

  def keys(self):
    return self.data.keys()

  def values(self):
    return self.data.values()

def validate(config):
  err = 'config.Config is a base class. Use config.{Small, Medium Large}'''
  assert isinstance(config, Config), err

  if not config.TERRAIN_SYSTEM_ENABLED:
    err = 'Invalid Config: {} requires Terrain'
    assert not config.RESOURCE_SYSTEM_ENABLED, err.format('Resource')
    assert not config.PROFESSION_SYSTEM_ENABLED, err.format('Profession')

  if not config.COMBAT_SYSTEM_ENABLED:
    err = 'Invalid Config: {} requires Combat'
    assert not config.NPC_SYSTEM_ENABLED, err.format('NPC')

  if not config.ITEM_SYSTEM_ENABLED:
    err = 'Invalid Config: {} requires Inventory'
    assert not config.EQUIPMENT_SYSTEM_ENABLED, err.format('Equipment')
    assert not config.PROFESSION_SYSTEM_ENABLED, err.format('Profession')
    assert not config.EXCHANGE_SYSTEM_ENABLED, err.format('Exchange')


class Config(Template):
  '''An environment configuration object

  Global constants are defined as static class variables. You can override
  any Config variable using standard CLI syntax (e.g. --NENT=128).

  The default config as of v1.5 uses 1024x1024 maps with up to 2048 agents
  and 1024 NPCs. It is suitable to time horizons of 8192+ steps. For smaller
  experiments, consider the SmallMaps config.

  Notes:
    We use Google Fire internally to replace standard manual argparse
    definitions for each Config property. This means you can subclass
    Config to add new static attributes -- CLI definitions will be
    generated automatically.
  '''

  def __init__(self):
    super().__init__()

    # TODO: Come up with a better way
    # to resolve mixin MRO conflicts
    if not hasattr(self, 'TERRAIN_SYSTEM_ENABLED'):
      self.TERRAIN_SYSTEM_ENABLED = False

    if not hasattr(self, 'RESOURCE_SYSTEM_ENABLED'):
      self.RESOURCE_SYSTEM_ENABLED = False

    if not hasattr(self, 'COMBAT_SYSTEM_ENABLED'):
      self.COMBAT_SYSTEM_ENABLED = False

    if not hasattr(self, 'NPC_SYSTEM_ENABLED'):
      self.NPC_SYSTEM_ENABLED = False

    if not hasattr(self, 'PROGRESSION_SYSTEM_ENABLED'):
      self.PROGRESSION_SYSTEM_ENABLED = False

    if not hasattr(self, 'ITEM_SYSTEM_ENABLED'):
      self.ITEM_SYSTEM_ENABLED = False

    if not hasattr(self, 'EQUIPMENT_SYSTEM_ENABLED'):
      self.EQUIPMENT_SYSTEM_ENABLED = False

    if not hasattr(self, 'PROFESSION_SYSTEM_ENABLED'):
      self.PROFESSION_SYSTEM_ENABLED = False

    if not hasattr(self, 'EXCHANGE_SYSTEM_ENABLED'):
      self.EXCHANGE_SYSTEM_ENABLED = False

    if not hasattr(self, 'COMMUNICATION_SYSTEM_ENABLED'):
      self.COMMUNICATION_SYSTEM_ENABLED = False

    if __debug__:
      validate(self)

    deprecated_attrs = [
      'NENT', 'NPOP', 'AGENTS', 'NMAPS', 'FORCE_MAP_GENERATION', 'SPAWN']

    for attr in deprecated_attrs:
      assert not hasattr(self, attr), f'{attr} has been deprecated or renamed'


  ############################################################################
  ### Meta-Parameters
  def game_system_enabled(self, name) -> bool:
    return hasattr(self, name)

  PROVIDE_ACTION_TARGETS       = True
  '''Provide action targets mask'''

  PROVIDE_NOOP_ACTION_TARGET   = True
  '''Provide a no-op option for each action'''

  PLAYERS                      = [Agent]
  '''Player classes from which to spawn'''

  HORIZON = 1024
  '''Number of steps before the environment resets'''

  CURRICULUM_FILE_PATH = None
  '''Path to a curriculum task file containing a list of task specs for training'''

  TASK_EMBED_DIM = 4096
  '''Dimensionality of task embeddings'''

  ALLOW_MULTI_TASKS_PER_AGENT = False
  '''Whether to allow multiple tasks per agent'''

  ############################################################################
  ### Population Parameters
  LOG_VERBOSE                  = False
  '''Whether to log server messages or just stats'''

  LOG_ENV                      = False
  '''Whether to log env steps (expensive)'''

  LOG_MILESTONES               = True
  '''Whether to log server-firsts (semi-expensive)'''

  LOG_EVENTS                   = True
  '''Whether to log events (semi-expensive)'''

  LOG_FILE                     = None
  '''Where to write logs (defaults to console)'''


  ############################################################################
  ### Player Parameters
  PLAYER_N                     = None
  '''Maximum number of players spawnable in the environment'''

  # TODO: CHECK if there could be 100+ entities within one's vision
  PLAYER_N_OBS                 = 100
  '''Number of distinct agent observations'''

  @property
  def PLAYER_POLICIES(self):
    '''Number of player policies'''
    return len(self.PLAYERS)

  PLAYER_BASE_HEALTH           = 100
  '''Initial agent health'''

  PLAYER_VISION_RADIUS         = 7
  '''Number of tiles an agent can see in any direction'''

  @property
  def PLAYER_VISION_DIAMETER(self):
    '''Size of the square tile crop visible to an agent'''
    return 2*self.PLAYER_VISION_RADIUS + 1

  PLAYER_DEATH_FOG             = None
  '''How long before spawning death fog. None for no death fog'''

  PLAYER_DEATH_FOG_SPEED       = 1
  '''Number of tiles per tick that the fog moves in'''

  PLAYER_DEATH_FOG_FINAL_SIZE  = 8
  '''Number of tiles from the center that the fog stops'''

  PLAYER_LOADER                = spawn.SequentialLoader
  '''Agent loader class specifying spawn sampling'''

  PLAYER_SPAWN_TEAMMATE_DISTANCE = 1
  '''Buffer tiles between teammates at spawn'''

  @property
  def PLAYER_TEAM_SIZE(self):
    if __debug__:
      assert not self.PLAYER_N % len(self.PLAYERS)
    return self.PLAYER_N // len(self.PLAYERS)

  ############################################################################
  ### Debug Parameters
  IMMORTAL = False
  '''Debug parameter: prevents agents from dying except by void'''

  RESET_ON_DEATH = False
  '''Debug parameter: whether to reset the environment whenever an agent dies'''

  ############################################################################
  ### Map Parameters
  MAP_N                        = 1
  '''Number of maps to generate'''

  MAP_N_TILE                   = len(material.All.materials)
  '''Number of distinct terrain tile types'''

  @property
  def MAP_N_OBS(self):
    '''Number of distinct tile observations'''
    return int(self.PLAYER_VISION_DIAMETER ** 2)

  MAP_CENTER                   = None
  '''Size of each map (number of tiles along each side)'''

  MAP_BORDER                   = 16
  '''Number of void border tiles surrounding each side of the map'''

  @property
  def MAP_SIZE(self):
    return int(self.MAP_CENTER + 2*self.MAP_BORDER)

  MAP_GENERATOR                = MapGenerator
  '''Specifies a user map generator. Uses default generator if unspecified.'''

  MAP_FORCE_GENERATION         = True
  '''Whether to regenerate and overwrite existing maps'''

  MAP_GENERATE_PREVIEWS        = False
  '''Whether map generation should also save .png previews (slow + large file size)'''

  MAP_PREVIEW_DOWNSCALE        = 1
  '''Downscaling factor for png previews'''


  ############################################################################
  ### Path Parameters
  PATH_ROOT                = os.path.dirname(nmmo.__file__)
  '''Global repository directory'''

  PATH_CWD                 = os.getcwd()
  '''Working directory'''

  PATH_RESOURCE            = os.path.join(PATH_ROOT, 'resource')
  '''Resource directory'''

  PATH_TILE                = os.path.join(PATH_RESOURCE, '{}.png')
  '''Tile path -- format me with tile name'''

  PATH_MAPS                = None
  '''Generated map directory'''

  PATH_MAP_SUFFIX          = 'map{}/map.npy'
  '''Map file name'''

  PATH_MAP_SUFFIX          = 'map{}/map.npy'
  '''Map file name'''


############################################################################
### Game Systems (Static Mixins)
class Terrain:
  '''Terrain Game System'''

  TERRAIN_SYSTEM_ENABLED       = True
  '''Game system flag'''

  TERRAIN_FLIP_SEED            = False
  '''Whether to negate the seed used for generation (useful for unique heldout maps)'''

  TERRAIN_FREQUENCY            = -3
  '''Base noise frequency range (log2 space)'''

  TERRAIN_FREQUENCY_OFFSET     = 7
  '''Noise frequency octave offset (log2 space)'''

  TERRAIN_LOG_INTERPOLATE_MIN  = -2
  '''Minimum interpolation log-strength for noise frequencies'''

  TERRAIN_LOG_INTERPOLATE_MAX  = 0
  '''Maximum interpolation log-strength for noise frequencies'''

  TERRAIN_TILES_PER_OCTAVE     = 8
  '''Number of octaves sampled from log2 spaced TERRAIN_FREQUENCY range'''

  TERRAIN_VOID                 = 0.0
  '''Noise threshold for void generation'''

  TERRAIN_WATER                = 0.30
  '''Noise threshold for water generation'''

  TERRAIN_GRASS                = 0.70
  '''Noise threshold for grass'''

  TERRAIN_FOILAGE              = 0.85
  '''Noise threshold for foilage (food tile)'''


class Resource:
  '''Resource Game System'''

  RESOURCE_SYSTEM_ENABLED             = True
  '''Game system flag'''

  RESOURCE_BASE                       = 100
  '''Initial level and capacity for food and water'''

  RESOURCE_DEPLETION_RATE             = 5
  '''Depletion rate for food and water'''

  RESOURCE_STARVATION_RATE            = 10
  '''Damage per tick without food'''

  RESOURCE_DEHYDRATION_RATE           = 10
  '''Damage per tick without water'''

  RESOURCE_RESILIENT_POPULATION       = 0
  '''Training helper: proportion of population that is resilient to starvation and dehydration
     (e.g. 0.1 means 10% of the population is resilient to starvation and dehydration)
     This is to make some agents live longer during training to sample from "advanced" agents.'''

  RESOURCE_DAMAGE_REDUCTION           = 0.5
  '''Training helper: damage reduction from starvation and dehydration for resilient agents'''

  RESOURCE_FOILAGE_CAPACITY           = 1
  '''Maximum number of harvests before a foilage tile decays'''

  RESOURCE_FOILAGE_RESPAWN            = 0.025
  '''Probability that a harvested foilage tile will regenerate each tick'''

  RESOURCE_HARVEST_RESTORE_FRACTION   = 1.0
  '''Fraction of maximum capacity restored upon collecting a resource'''

  RESOURCE_HEALTH_REGEN_THRESHOLD     = 0.5
  '''Fraction of maximum resource capacity required to regen health'''

  RESOURCE_HEALTH_RESTORE_FRACTION    = 0.1
  '''Fraction of health restored per tick when above half food+water'''


class Combat:
  '''Combat Game System'''

  COMBAT_SYSTEM_ENABLED              = True
  '''Game system flag'''

  COMBAT_SPAWN_IMMUNITY              = 20
  '''Agents older than this many ticks cannot attack agents younger than this many ticks'''

  COMBAT_STATUS_DURATION             = 3
  '''Combat status lasts for this many ticks after the last combat event.
     Combat events include both attacking and being attacked.'''

  COMBAT_WEAKNESS_MULTIPLIER         = 1.5
  '''Multiplier for super-effective attacks'''

  def COMBAT_DAMAGE_FORMULA(self, offense, defense, multiplier):
    '''Damage formula'''
    return int(multiplier * (offense * (15 / (15 + defense))))

  COMBAT_MELEE_DAMAGE                = 30
  '''Melee attack damage'''

  COMBAT_MELEE_REACH                 = 3
  '''Reach of attacks using the Melee skill'''

  COMBAT_RANGE_DAMAGE                = 30
  '''Range attack damage'''

  COMBAT_RANGE_REACH                 = 3
  '''Reach of attacks using the Range skill'''

  COMBAT_MAGE_DAMAGE                 = 30
  '''Mage attack damage'''

  COMBAT_MAGE_REACH                  = 3
  '''Reach of attacks using the Mage skill'''


def default_exp_threshold(max_level):
  import math
  additional_exp_per_level = [round(90*math.sqrt(lvl))
                              for lvl in range(1, max_level+1)]
  return [sum(additional_exp_per_level[:lvl]) for lvl in range(max_level)]

class Progression:
  '''Progression Game System'''

  PROGRESSION_SYSTEM_ENABLED        = True
  '''Game system flag'''

  PROGRESSION_BASE_LEVEL            = 1
  '''Initial skill level'''

  PROGRESSION_LEVEL_MAX             = 10
  '''Max skill level'''

  PROGRESSION_EXP_THRESHOLD         = default_exp_threshold(PROGRESSION_LEVEL_MAX)
  '''A list of experience thresholds for each level'''

  PROGRESSION_COMBAT_XP_SCALE       = 3
  '''Additional XP for each attack for skills Melee, Range, and Mage'''

  PROGRESSION_AMMUNITION_XP_SCALE   = 15
  '''Additional XP for each harvest for Prospecting, Carving, and Alchemy'''

  PROGRESSION_CONSUMABLE_XP_SCALE   = 30
  '''Multiplier XP for each harvest for Fishing and Herbalism'''

  PROGRESSION_MELEE_BASE_DAMAGE     = 20
  '''Base Melee attack damage'''

  PROGRESSION_MELEE_LEVEL_DAMAGE    = 5
  '''Bonus Melee attack damage per level'''

  PROGRESSION_RANGE_BASE_DAMAGE     = 20
  '''Base Range attack damage'''

  PROGRESSION_RANGE_LEVEL_DAMAGE    = 5
  '''Bonus Range attack damage per level'''

  PROGRESSION_MAGE_BASE_DAMAGE      = 20
  '''Base Mage attack damage '''

  PROGRESSION_MAGE_LEVEL_DAMAGE     = 5
  '''Bonus Mage attack damage per level'''

  PROGRESSION_BASE_DEFENSE          = 0
  '''Base defense'''

  PROGRESSION_LEVEL_DEFENSE         = 5
  '''Bonus defense per level'''


class NPC:
  '''NPC Game System'''

  NPC_SYSTEM_ENABLED                  = True
  '''Game system flag'''

  NPC_N                               = None
  '''Maximum number of NPCs spawnable in the environment'''

  NPC_SPAWN_ATTEMPTS                  = 25
  '''Number of NPC spawn attempts per tick'''

  NPC_SPAWN_AGGRESSIVE                = 0.80
  '''Percentage distance threshold from spawn for aggressive NPCs'''

  NPC_SPAWN_NEUTRAL                   = 0.50
  '''Percentage distance threshold from spawn for neutral NPCs'''

  NPC_SPAWN_PASSIVE                   = 0.00
  '''Percentage distance threshold from spawn for passive NPCs'''

  NPC_LEVEL_MIN                       = 1
  '''Minimum NPC level'''

  NPC_LEVEL_MAX                       = 10
  '''Maximum NPC level'''

  NPC_BASE_DEFENSE                    = 0
  '''Base NPC defense'''

  NPC_LEVEL_DEFENSE                   = 15
  '''Bonus NPC defense per level'''

  NPC_BASE_DAMAGE                     = 15
  '''Base NPC damage'''

  NPC_LEVEL_DAMAGE                    = 15
  '''Bonus NPC damage per level'''


class Item:
  '''Inventory Game System'''

  ITEM_SYSTEM_ENABLED                 = True
  '''Game system flag'''

  ITEM_N                              = 17
  '''Number of unique base item classes'''

  ITEM_INVENTORY_CAPACITY             = 12
  '''Number of inventory spaces'''

  ITEM_ALLOW_GIFT               = True
  '''Whether agents can give gold/item to each other'''

  @property
  def INVENTORY_N_OBS(self):
    '''Number of distinct item observations'''
    return self.ITEM_INVENTORY_CAPACITY


class Equipment:
  '''Equipment Game System'''

  EQUIPMENT_SYSTEM_ENABLED             = True
  '''Game system flag'''

  WEAPON_DROP_PROB = 0.025
  '''Chance of getting a weapon while harvesting ammunition'''

  EQUIPMENT_WEAPON_BASE_DAMAGE         = 15
  '''Base weapon damage'''

  EQUIPMENT_WEAPON_LEVEL_DAMAGE        = 15
  '''Added weapon damage per level'''

  EQUIPMENT_AMMUNITION_BASE_DAMAGE     = 15
  '''Base ammunition damage'''

  EQUIPMENT_AMMUNITION_LEVEL_DAMAGE    = 15
  '''Added ammunition damage per level'''

  EQUIPMENT_TOOL_BASE_DEFENSE          = 30
  '''Base tool defense'''

  EQUIPMENT_TOOL_LEVEL_DEFENSE         = 0
  '''Added tool defense per level'''

  EQUIPMENT_ARMOR_BASE_DEFENSE         = 0
  '''Base armor defense'''

  EQUIPMENT_ARMOR_LEVEL_DEFENSE        = 10
  '''Base equipment defense'''


class Profession:
  '''Profession Game System'''

  PROFESSION_SYSTEM_ENABLED           = True
  '''Game system flag'''

  PROFESSION_TREE_CAPACITY            = 1
  '''Maximum number of harvests before a tree tile decays'''

  PROFESSION_TREE_RESPAWN             = 0.105
  '''Probability that a harvested tree tile will regenerate each tick'''

  PROFESSION_ORE_CAPACITY             = 1
  '''Maximum number of harvests before an ore tile decays'''

  PROFESSION_ORE_RESPAWN              = 0.10
  '''Probability that a harvested ore tile will regenerate each tick'''

  PROFESSION_CRYSTAL_CAPACITY         = 1
  '''Maximum number of harvests before a crystal tile decays'''

  PROFESSION_CRYSTAL_RESPAWN          = 0.10
  '''Probability that a harvested crystal tile will regenerate each tick'''

  PROFESSION_HERB_CAPACITY            = 1
  '''Maximum number of harvests before an herb tile decays'''

  PROFESSION_HERB_RESPAWN             = 0.02
  '''Probability that a harvested herb tile will regenerate each tick'''

  PROFESSION_FISH_CAPACITY            = 1
  '''Maximum number of harvests before a fish tile decays'''

  PROFESSION_FISH_RESPAWN             = 0.02
  '''Probability that a harvested fish tile will regenerate each tick'''

  @staticmethod
  def PROFESSION_CONSUMABLE_RESTORE(level):
    return 50 + 5*level


class Exchange:
  '''Exchange Game System'''

  EXCHANGE_SYSTEM_ENABLED             = True
  '''Game system flag'''

  EXCHANGE_BASE_GOLD                  = 1
  '''Initial gold amount'''

  EXCHANGE_LISTING_DURATION           = 5
  '''The number of ticks, during which the item is listed for sale'''

  MARKET_N_OBS = 1024
  '''Number of distinct item observations'''

  PRICE_N_OBS = 99 # make it different from PLAYER_N_OBS
  '''Number of distinct price observations
     This also determines the maximum price one can set for an item
  '''


class Communication:
  '''Exchange Game System'''

  COMMUNICATION_SYSTEM_ENABLED             = True
  '''Game system flag'''

  # CHECK ME: When do we actually use this?
  COMMUNICATION_NUM_TOKENS                 = 50
  '''Number of distinct COMM tokens'''


class AllGameSystems(
  Terrain, Resource, Combat, NPC, Progression, Item,
  Equipment, Profession, Exchange, Communication):
  pass


############################################################################
### Config presets
class Small(Config):
  '''A small config for debugging and experiments with an expensive outer loop'''

  PATH_MAPS                    = 'maps/small'

  PLAYER_N                     = 64

  MAP_PREVIEW_DOWNSCALE        = 4
  MAP_CENTER                   = 32

  TERRAIN_LOG_INTERPOLATE_MIN  = 0

  NPC_N                        = 32
  NPC_LEVEL_MAX                = 5
  NPC_LEVEL_SPREAD             = 1

  PROGRESSION_SPAWN_CLUSTERS   = 4
  PROGRESSION_SPAWN_UNIFORMS   = 16

  HORIZON                      = 128


class Medium(Config):
  '''A medium config suitable for most academic-scale research'''

  PATH_MAPS                    = 'maps/medium'

  PLAYER_N                     = 128

  MAP_PREVIEW_DOWNSCALE        = 16
  MAP_CENTER                   = 128

  NPC_N                        = 128
  NPC_LEVEL_MAX                = 10
  NPC_LEVEL_SPREAD             = 1

  PROGRESSION_SPAWN_CLUSTERS   = 64
  PROGRESSION_SPAWN_UNIFORMS   = 256

  HORIZON                      = 1024


class Large(Config):
  '''A large config suitable for large-scale research or fast models'''

  PATH_MAPS                    = 'maps/large'

  PLAYER_N                     = 1024

  MAP_PREVIEW_DOWNSCALE        = 64
  MAP_CENTER                   = 1024

  NPC_N                        = 1024
  NPC_LEVEL_MAX                = 15
  NPC_LEVEL_SPREAD             = 3

  PROGRESSION_SPAWN_CLUSTERS   = 1024
  PROGRESSION_SPAWN_UNIFORMS   = 4096

  HORIZON                 = 8192


class Default(Medium, AllGameSystems):
  pass
