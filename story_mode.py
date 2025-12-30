
import pygame
from dataclasses import dataclass
from typing import List, Dict, Callable

@dataclass
class Challenge:
    """Represents a challenge constraint in a story"""
    type: str  # 'limited_bullets', 'time_limit', 'no_damage', 'accuracy', 'speed_run'
    value: int  # Specific value for the challenge
    description: str
    active: bool = True
    
@dataclass
class Wave:
    """Represents an enemy wave in a story"""
    enemy_count: int
    enemy_types: List[str]  # ['basic', 'tank', 'fast', 'shooter']
    spawn_interval: int  # milliseconds
    meteor_count: int = 0
    
@dataclass
class StoryData:
    """Complete story configuration"""
    id: int
    title: str
    subtitle: str
    description: str
    narrative: List[str]  # Story text shown at start/during gameplay
    challenges: List[Challenge]
    waves: List[Wave]
    background_color: tuple
    difficulty_multiplier: float
    power_up_spawn_rate: int  # milliseconds
    power_down_spawn_rate: int  # milliseconds
    completion_reward: int  # bonus score

class StoryMode:
    """Manages story mode progression and state"""
    
    def __init__(self):
        self.current_story = None
        self.current_wave_index = 0
        self.story_active = False
        self.story_complete = False
        self.challenges_status = {}
        self.narrative_index = 0
        self.show_narrative = False
        self.narrative_timer = 0
        self.story_start_time = 0
        self.pause_start_time = 0
        self.total_pause_time = 0
        
        # Story definitions
        self.stories = self._create_stories()
        
    def _create_stories(self) -> Dict[int, StoryData]:
        """Create all story configurations"""
        stories = {}
        
        # STORY 1: The Asteroid Belt Ambush
        stories[1] = StoryData(
            id=1,
            title="THE ASTEROID BELT",
            subtitle="Ambush in the Void",
            description="Navigate through a dense asteroid field while enemy scouts attack!",
            narrative=[
                "MISSION BRIEFING:",
                "Enemy scouts detected in Sector 7.",
                "Navigate the asteroid belt and eliminate all threats.",
                "WARNING: Limited ammunition - make every shot count!",
            ],
            challenges=[
                Challenge('limited_bullets', 50, "Limited Ammo: 50 shots only"),
                Challenge('time_limit', 120, "Time Limit: 2 minutes"),
            ],
            waves=[
                Wave(enemy_count=5, enemy_types=['basic'], spawn_interval=2000, meteor_count=10),
                Wave(enemy_count=8, enemy_types=['basic', 'fast'], spawn_interval=1500, meteor_count=15),
                Wave(enemy_count=10, enemy_types=['basic', 'fast', 'shooter'], spawn_interval=1200, meteor_count=20),
            ],
            background_color=(10, 10, 30),
            difficulty_multiplier=1.0,
            power_up_spawn_rate=15000,
            power_down_spawn_rate=20000,
            completion_reward=5000
        )
        
        # STORY 2: The Fleet Invasion
        stories[2] = StoryData(
            id=2,
            title="THE FLEET INVASION",
            subtitle="Battle for Survival",
            description="The enemy fleet has arrived! Face waves of advanced fighters and heavy cruisers.",
            narrative=[
                "URGENT TRANSMISSION:",
                "Enemy fleet approaching at high speed!",
                "Multiple heavy cruisers and fighter squadrons detected.",
                "WARNING: Rapid fire required - conserve your shots!",
                "Power-ups available - use them wisely!",
            ],
            challenges=[
                Challenge('limited_bullets', 80, "Limited Ammo: 80 shots"),
                Challenge('shoot_cooldown', 400, "Slower Fire Rate: 400ms cooldown"),
                Challenge('time_limit', 150, "Time Limit: 2.5 minutes"),
            ],
            waves=[
                Wave(enemy_count=12, enemy_types=['basic', 'shooter'], spawn_interval=1500, meteor_count=5),
                Wave(enemy_count=15, enemy_types=['fast', 'shooter', 'tank'], spawn_interval=1200, meteor_count=8),
                Wave(enemy_count=10, enemy_types=['tank', 'shooter'], spawn_interval=1000, meteor_count=5),
                Wave(enemy_count=20, enemy_types=['basic', 'fast', 'shooter', 'tank'], spawn_interval=800, meteor_count=10),
            ],
            background_color=(15, 5, 25),
            difficulty_multiplier=1.5,
            power_up_spawn_rate=12000,
            power_down_spawn_rate=18000,
            completion_reward=10000
        )
        
        return stories
    
    def start_story(self, story_id: int):
        """Initialize a story"""
        if story_id not in self.stories:
            return False
            
        self.current_story = self.stories[story_id]
        self.current_wave_index = 0
        self.story_active = True
        self.story_complete = False
        self.narrative_index = 0
        self.show_narrative = True
        self.narrative_timer = pygame.time.get_ticks()
        self.pause_start_time = pygame.time.get_ticks()
        self.total_pause_time = 0
        
        # Initialize challenge status
        self.challenges_status = {}
        for challenge in self.current_story.challenges:
            self.challenges_status[challenge.type] = {
                'active': True,
                'current_value': challenge.value,
                'max_value': challenge.value,
                'failed': False
            }
        
        return True
    
    def get_current_wave(self) -> Wave:
        """Get the current wave configuration"""
        if not self.current_story or self.current_wave_index >= len(self.current_story.waves):
            return None
        return self.current_story.waves[self.current_wave_index]
    
    def advance_wave(self):
        """Move to the next wave"""
        self.current_wave_index += 1
        if self.current_wave_index >= len(self.current_story.waves):
            self.complete_story()
    
    def complete_story(self):
        """Mark story as complete"""
        self.story_complete = True
        self.story_active = False
    
    def update_challenge(self, challenge_type: str, value: int):
        """Update challenge progress"""
        if challenge_type in self.challenges_status:
            self.challenges_status[challenge_type]['current_value'] = value
            
            # Check if challenge failed
            if challenge_type == 'limited_bullets' and value <= 0:
                self.challenges_status[challenge_type]['failed'] = True
            elif challenge_type == 'time_limit' and value <= 0:
                self.challenges_status[challenge_type]['failed'] = True
    
    def is_challenge_failed(self) -> bool:
        """Check if any challenge has failed"""
        return any(status['failed'] for status in self.challenges_status.values())
    
    def get_narrative_text(self) -> str:
        """Get current narrative text to display"""
        if not self.current_story or self.narrative_index >= len(self.current_story.narrative):
            return ""
        return self.current_story.narrative[self.narrative_index]
    
    def advance_narrative(self):
        """Move to next narrative text"""
        self.narrative_index += 1
        if self.narrative_index >= len(self.current_story.narrative):
            self.show_narrative = False
            # Track pause time
            if self.pause_start_time > 0:
                self.total_pause_time += pygame.time.get_ticks() - self.pause_start_time
                self.pause_start_time = 0
    
    def get_all_stories(self) -> List[StoryData]:
        """Get list of all available stories"""
        return list(self.stories.values())
