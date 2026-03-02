"""
interaction_engine.py — Manages dialogue selection, cooldowns,
tone switching, and repetition avoidance.

Tones available:
  pub_banter   — cheeky, funny, ideal for a pub setting
  welcoming    — warm and friendly
  mysterious   — theatrical and enigmatic
  cheeky       — playful and irreverent
  mixed        — combines ALL tones for maximum variety (ideal for 150+ people venues)
"""

import time
import random
import logging
import re

log = logging.getLogger("interaction_engine")

# ── Dialogue Library ──

LINES = {
    "pub_banter": {
        "solo": [
            "Oi! Drinking alone are we? Don't worry, you've got me.",
            "Looking good! The mirror never lies... much.",
            "You walked in like you own the place. I respect that.",
            "Ah, a lone wolf. The most dangerous kind.",
            "Don't just stand there — the bar's that way.",
            "Is that your best outfit? Bold choice. Very bold.",
            "You look like you need a pint. Am I wrong?",
            "Chin up, gorgeous. You walked in here, didn't you?",
            "Right then. Are you staying for one or staying for the whole match?",
            "Last time I saw someone that confident, they bought a round. Just saying.",
            "Well well well, look who decided to show up.",
            "Flying solo here? Brave move.",
            "You've got that 'I know what I'm doing' look. I like it.",
            "Walking in here like it's no big deal. Smooth.",
            "Let me guess — first drink or third?",
            "Alright! Someone who knows what they want.",
            "You look like you've got a good story or two.",
            "Just you and me, then. I'm excellent company.",
            "Right, so are we celebrating or commiserating?",
            "Independent spirit! Love to see it.",
            "You've got that Friday feeling, don't you?",
            "Fancy seeing you here. What's the occasion?",
            "Someone's on a solo mission? Respect the confidence.",
            "You look like someone who doesn't need an excuse to go out.",
            "That entrance though. Ten out of ten.",
            "Are we starting strong or pacing ourselves today?",
            "You walked in like you've been here before. Have you?",
            "Looking sharp! Someone's going to notice.",
            "Alright, legend. What are we drinking?",
            "You seem like you know your way around a good time.",
        ],
        "group": [
            "Oh it's a whole crew! Someone's getting the first round in.",
            "Look at this lot! Who's the designated driver? Tough luck.",
            "A group this size? Someone's definitely getting a dodgy photo taken today.",
            "Welcome, welcome to Blah Bla X! The more the merrier — and the louder.",
            "Right, who convinced everyone else to come out? You're the hero for today.",
            "Look at you all! Someone's going home with a great story.",
            "A group! Brilliant. The bar staff are already nervous.",
            "Now THIS is a party. Or at least the warm-up for one.",
            "Gang's all here! Who ordered the fun?",
            "Right, which one of you is buying the first round?",
            "A whole squad! This is going to be a good time.",
            "Look at this crew! Already causing a scene, I love it.",
            "Everyone showed up! That's commitment.",
            "Oh no, you brought reinforcements!",
            "Group of legends just walked in. Noted.",
            "Right, who's the ringleader of this operation?",
            "This many people? Someone's celebrating something.",
            "The energy just doubled. Welcome, everyone!",
            "Brilliant! A group means double the chaos.",
            "Who convinced everyone to leave the house? Well done.",
            "Squad goals right here. Looking good, all of you!",
            "A full crew! The bar better be ready.",
            "Right, who's telling the best stories today?",
            "Look at you all! This is what fun looks like.",
            "Gang assembled! Let's make this one memorable.",
        ],
    },
    "welcoming": {
        "solo": [
            "Welcome in! Hope you find exactly what you're looking for today at Blah Bla X.",
            "Great to see you! Make yourself at home.",
            "Come on in — you look like you deserve a good break from your day.",
            "Hey there! The best days always start just like this.",
            "Welcome to Blah Bla X! Today's going to be a good one, I can feel it.",
            "Hello! So glad you're here.",
            "Welcome! Pull up a seat and enjoy yourself.",
            "Great timing! You're going to love it here.",
            "Hey! You picked the right place today.",
            "Welcome to Blah Bla X — we've been waiting for you!",
            "Come in, come in! Let's make today special.",
            "Hello there! Ready for a wonderful time ?",
            "Welcome! The vibe is just right today.",
            "So happy you're here! Enjoy every moment.",
            "Hey! Today's all about you — have fun!",
            "Welcome in! This is going to be great.",
            "Hi there! You're exactly where you need to be.",
            "Welcome to Blah Bla X! Let's make some memories.",
            "Great to have you! Enjoy your time here at Blah Bla X.",
            "Hello! The day is young — make the most of it.",
            "Welcome! You're in for a treat today.",
            "Hi! So pleased you decided to stop by.",
            "Welcome in! Today's looking bright already.",
            "Hey there! Let the good times begin.",
            "Welcome to Blah Bla X — your fun starts now!",
        ],
        "group": [
            "What a lovely group! Welcome to Blah Bla X, everyone.",
            "Great to have you all here — the more the merrier!",
            "Welcome in! Looks like today just got a lot more fun at Blah Bla X.",
            "What a crew! Hope you all have a brilliant time.",
            "Hello everyone! So wonderful to see you all.",
            "Welcome, welcome! This is going to be fantastic.",
            "What a great group! Come on in, all of you.",
            "Hi everyone! Today's going to be special with you here.",
            "Welcome to Blah Bla X! Your group just lit up the place.",
            "So happy to see you all! Enjoy every moment together.",
            "What a lovely bunch! Welcome, everyone.",
            "Hello! Your group energy is already amazing.",
            "Welcome in! This many people means serious fun ahead.",
            "Great to have you all! Let's make today unforgettable.",
            "Hi everyone! The vibe just got even better.",
            "Welcome, friends! Today is yours to enjoy.",
            "What a wonderful group! Come in and have a blast.",
            "Hello all! Your great time starts right here, right now.",
            "Welcome to Blah Bla X! So glad you're all here together.",
            "Hi there, everyone! Let the celebrations begin!",
        ],
    },
    "mysterious": {
        "solo": [
            "I've been watching this mirror for years... you're the most interesting one yet.",
            "The mirror sees all. And right now, it sees you.",
            "They say mirrors reflect the truth. Shall we test that theory?",
            "You arrive. The mirror remembers. Curious.",
            "There are no accidents. You standing here — that means something.",
            "Another soul drawn to the mirror. Why, I wonder?",
            "The glass knows your face now. It won't forget.",
            "Interesting. The mirror doesn't speak to just anyone.",
            "You've crossed the threshold. The mirror has chosen you.",
            "Time slows here. The mirror notices everything.",
            "Your reflection tells a story. I'm listening.",
            "The mirror sees beyond the surface. Always has.",
            "You feel it too, don't you? The mirror's pull.",
            "Fate brought you here. Or was it something else?",
            "The mirror has been waiting. For you. For this moment.",
            "Look closer. The mirror reveals what you hide.",
            "You're not the first to stand here. But you might be different.",
            "The mirror whispers secrets. Do you hear them?",
            "Something about you... the mirror is intrigued.",
            "Welcome to the space between. The mirror sees you clearly.",
            "The reflection never lies. Neither do I.",
            "You walked in like you knew. Perhaps you did.",
            "The mirror has seen thousands. You... stand out.",
            "Time bends here. The mirror bends with it.",
            "You came seeking answers. The mirror provides questions.",
        ],
        "group": [
            "A gathering. Fate rarely sends so many at once... interesting.",
            "The mirror wasn't expecting a group. Neither was I. And yet, here we all are.",
            "Many faces. One mirror. The possibilities are... intriguing.",
            "A group steps forward. The space shifts. Can you feel it?",
            "Together you stand before the mirror. Together, perhaps, you'll understand.",
            "The mirror sees all of you. Every secret. Every truth.",
            "How curious. Multiple souls drawn to the same moment.",
            "A collective energy. The mirror feeds on this.",
            "You came together. The mirror knows why.",
            "Many reflections. One truth. The mirror will reveal it.",
            "The group dynamic... the mirror finds it fascinating.",
            "You're connected. The mirror sees the threads between you.",
            "Together before the mirror. What will it show you?",
            "The mirror rarely sees groups. This is... special.",
            "Multiple presences. The mirror is listening to all of you.",
            "You arrived as one. The mirror will remember.",
            "A gathering of souls. The mirror approves.",
            "Together you face the glass. Brave. Or foolish?",
            "The mirror sees your bond. It's stronger than you think.",
            "Many enter. The mirror sees them all. Including you.",
        ],
    },
    "cheeky": {
        "solo": [
            "Oh nice — you actually stopped to check yourself out. Respect.",
            "You again! ...Wait, is this your first time? You have one of those faces.",
            "The mirror called. It wants you to know you're doing great, sweetie.",
            "Quick vanity check? Smart. Very smart.",
            "Just between us — you look brilliant. Don't let it go to your head.",
            "Someone's feeling themselves today. Good!",
            "Looking in the mirror? Can't blame you.",
            "Oh, hello gorgeous. Yes, I'm talking to you.",
            "Checking yourself out? I don't blame you one bit.",
            "Confidence level: off the charts. Love it.",
            "Did you just wink at yourself? Iconic.",
            "You walked in like you're already famous. Are you?",
            "Mirror check! And you passed with flying colours.",
            "Oh, you know you look good. I can tell.",
            "Somebody woke up and chose excellence today.",
            "Are you always this fabulous or is today special?",
            "The mirror approves. Highly.",
            "You're giving main character energy. Keep it up.",
            "Just so you know — yeah, you've still got it.",
            "Did someone tell you that you look great? Because they should have.",
            "The mirror's been waiting for someone this fun.",
            "You look like you're about to have the best time ever.",
            "Oh, we've got a confident one here! Finally!",
            "The mirror likes you. That's rare, actually.",
            "Are you always this cool or did you prepare for today?",
        ],
        "group": [
            "A whole group at the mirror at once? Someone's very confident.",
            "Group selfie incoming in 3... 2...",
            "I see you. All of you. Who's the most photogenic? The mirror knows.",
            "One of you is definitely the funniest. One of you thinks it's them. They're wrong.",
            "Oh, a squad! Are you all this cool or just here?",
            "Right, which one of you convinced everyone else? Genius move.",
            "Group photo time? The mirror is ready. Are you?",
            "The whole crew checking themselves out at once. Respect.",
            "One of you is the leader. The mirror can tell.",
            "A full group of legends. The mirror is impressed.",
            "Oh brilliant, a group that knows how to have fun!",
            "Who's the troublemaker? The mirror always spots them.",
            "You all look great. Just saying.",
            "A whole crew! Someone planned this perfectly.",
            "The mirror sees confidence. Lots of it. From all of you.",
            "Group energy is off the charts! Love to see it.",
            "Right, who's making everyone laugh today?",
            "You're all at the mirror? That's main character behaviour.",
            "The mirror likes you all. That's saying something.",
            "This group? Chef's kiss. Perfection.",
        ],
    },
}


class InteractionEngine:
    def __init__(self, cfg: dict):
        self.cooldown_seconds = cfg.get("cooldown_seconds", 8)
        self.max_repeats      = cfg.get("max_repeats_before_shuffle", 3)
        self.tone             = cfg.get("tone", "pub_banter")

        self._last_spoken_at   = 0.0
        self._solo_pool        = []
        self._group_pool       = []
        self._last_solo_line   = None
        self._last_group_line  = None

        self._reload_pools()
        log.info(f"Interaction engine ready (tone={self.tone})")

    def _reload_pools(self):
        """Load dialogue lines from either single tone or mix all tones."""
        if self.tone == "mixed":
            # Mix all tones together for maximum variety (150+ people)
            all_solo = []
            all_group = []
            for tone_name, tone_lines in LINES.items():
                all_solo.extend(tone_lines["solo"])
                all_group.extend(tone_lines["group"])
            self._solo_pool = all_solo.copy()
            self._group_pool = all_group.copy()
            log.info(f"Mixed mode: {len(self._solo_pool)} solo + {len(self._group_pool)} group lines loaded")
        else:
            # Single tone mode
            tone_lines = LINES.get(self.tone, LINES["pub_banter"])
            self._solo_pool = tone_lines["solo"].copy()
            self._group_pool = tone_lines["group"].copy()
        
        random.shuffle(self._solo_pool)
        random.shuffle(self._group_pool)

    def _pick(self, pool: list, last: str | None) -> tuple[str | None, list]:
        """Pick next line from pool, avoiding consecutive repeats."""
        if not pool:
            self._reload_pools()
            # After reload, use the fresh pools
            if last and hasattr(self, '_solo_pool') and last in self._solo_pool:
                pool = self._solo_pool.copy()
            elif hasattr(self, '_group_pool'):
                pool = self._group_pool.copy()
            random.shuffle(pool)

        # Avoid repeating the very last line
        candidates = [l for l in pool if l != last] or pool
        line = candidates[0]
        pool = [l for l in pool if l != line]
        return line, pool

    def get_line(self, face_count: int) -> str | None:
        """
        Returns a dialogue line if cooldown has elapsed, else None.
        face_count=1 → solo line; face_count>1 → group line.
        """
        now = time.time()
        if now - self._last_spoken_at < self.cooldown_seconds:
            return None

        if face_count == 1:
            line, self._solo_pool = self._pick(self._solo_pool, self._last_solo_line)
            self._last_solo_line = line
        else:
            line, self._group_pool = self._pick(self._group_pool, self._last_group_line)
            self._last_group_line = line

        self._last_spoken_at = now
        return line

    def set_tone(self, tone: str):
        """Hot-swap the tone at runtime."""
        if tone != "mixed" and tone not in LINES:
            log.warning(f"Unknown tone '{tone}' — keeping current")
            return
        self.tone = tone
        self._reload_pools()
        log.info(f"Tone changed to: {tone}")

    def get_response(self, user_text: str) -> str:
        """
        Generate a conversational response based on what the user said.
        Uses simple keyword matching + fallbacks for a natural pub conversation.
        Returns a response that feels contextual and ends the interaction gracefully.
        """
        user_lower = user_text.lower()
        
        # ── Greetings & Exclamations ───
        if any(w in user_lower for w in ["hello", "hi ", "hey", "good morning", "good evening", "omg", "oh my god", "wow", "whoa", "yikes", "lol", "lmao", "haha", "hehe"]):
            return random.choice([
                "Well hello to you too! Enjoy yourself.",
                "Cheers! Have a great one.",
                "Lovely to chat — now off you go, the bar's waiting.",
                "I am just a mirror, but I can tell you look fantastic. Now go have fun!",
                "Haha! Glad I could surprise you. Off you pop!",
                "Wow indeed! The day is young, enjoy it to the fullest.",
            ])
        
        # ── Scared / Surprised ──
        if any(w in user_lower for w in ["scare", "scared", "creepy", "weird", "no way", "seriously", "unbelievable"]):
            return random.choice([
                "Don't be scared — I'm just a mirror. But I do know how to have a good time. Off you go!",
                "I get that a lot. Don't worry, I'm friendly. Now go enjoy yourself!",
                "Not what you expected? Good. That's the point. Have a brilliant time!",
                "I can be a bit surprising, can't I? But I promise I'm on your side. Now go have fun!",
                "I know, it's a bit unusual. But that's what makes it fun, right? Enjoy!",

            ])
        
        # ── Thanks ──
        if any(w in user_lower for w in ["thank", "thanks", "cheers"]):
            return random.choice([
                "You're very welcome! Now go have fun.",
                "Pleasure's all mine. Off you go!",
                "Anytime! Enjoy your time here.",
            ])
        
        # ── Questions about the mirror ──
        if any(phrase in user_lower for phrase in ["who are you", "what are you", "your name", "are you real", "how do you work"]):
            return random.choice([
                "I'm the magic mirror. Been watching this place for years. Nice to meet you.",
                "Just a friendly mirror. Nothing fancy. Well... maybe a little fancy.",
                "I'm the mirror. And you're the lucky one I decided to talk to today.",
                "I see everything, but I don't say much. Until now, that is.",
                "A mirror with a voice? I know, it's a bit unusual. But I'm here to make your day better. Now go enjoy yourself!",
                "I work in mysterious ways. But mostly, I just want you to have a great time. Off you go!",
            ])
        
        # ── Compliments from user ──
        if any(w in user_lower for w in ["cool", "awesome", "amazing", "brilliant", "love it", "fantastic", "great"]):
            return random.choice([
                "Right back at you! Now go enjoy the pub.",
                "Appreciate that! You're alright yourself.",
                "Cheers! I do my best. Now off you pop.",
            ])
        
        # ── Actual questions (starts with question word or has ?)__
        if "?" in user_text or any(user_lower.startswith(w + " ") for w in ["what", "where", "when", "how", "why", "who", "can", "do you", "are you", "is this", "will you"]):
            return random.choice([
                "Good question. The answer is: go ask the bartender, they know everything.",
                "Hmm, mystery! I'm just a mirror. But you'll figure it out.",
                "That's above my pay grade. I just reflect and chat. You're on your own for that one!",
            ])
        
        # ── Jokes / Banter ─
        if any(w in user_lower for w in ["funny", "joke", "laugh"]):
            return random.choice([
                "I've got a million of 'em. But I'll spare you. Go enjoy your drink instead.",
                "Glad you're amused! Right, off you go now.",
                "I try! Now get out there, the fun's not in here with me.",
            ])
        
        #─── User indicates they want to end the conversation or are not interested ──
        if any(w in user_lower for w in ["no", "nope", "nah", "not really"]):
            return random.choice([
                "It's okay , Enjoy the pub!.",
                "maybe next time! I'll let you get on with it. Enjoy the pub!",
                "maybe I said too much? I'll let you get on with it. Enjoy the pub!",
            ])
        
        # ── Negativity / Complaints ───
        if any(w in user_lower for w in ["hate", "eww", "annoying", "shut up", "stupid", "bad", "worst"]):
            return random.choice([
                "Fair enough. I'll leave you to it then. Enjoy your time here.",
                "Noted. I'll pipe down. Have a good one!",
                "Alright, alright, I can take a hint. Go on then.",
            ])
        
          # ── Leaves the place saying bye/Unintrested ──
        if any(phrase in user_lower for phrase in ["bye", "goodbye", "see you later", "see you soon", "later", "see you tomorrow","bye-bye","bubye"]):
            return random.choice([
                "See you later! Have a great time!",
                "Goodbye! Enjoy the rest of your time here!",
                "Take care! I'll be here if you need me.",

            ])
          # ── Accpeting/Acknowledging ───
        if any(w in user_lower for w in ["yes", "yeahhh", "yep", "sure", "definitely", "absolutely", "of course", "right", "got it", "ok", "okay","ok ok","fine"]):
            return random.choice([
                "Great! Now go have fun.",
                "I knew it , You are a charm!",
                "Love your enthusiasm!, Now off you go!",
                "Right on! Enjoy your time here.",
            ])
        
        # ── Generic fallback (mirror doesn't understand) ───
        return random.choice([
            "Interesting point! Anyway, lovely chatting. Off you go now!",
            "Right you are. Well, enjoy the rest of your drink!",
            "Good stuff. Alright, I'll let you get on with it. Cheers!",
            "I'm not sure I follow, but I like your style. Now go have fun!",
            "The pub's  great, you'll know when you've had enough. Enjoy it while it lasts!",
            "I hear you! Now go have fun, the pub's waiting.",
            "Can't argue with that. Right, off you pop. Have a brilliant time!",
            "I see what you mean. Now go enjoy yourself, the bar's that way.",
            "Fair point! Now, let's get back to the important stuff — enjoying your time here.",
            "You make a good point. Now go have fun, the mirror will be here when you get back.",
            "I understand. Now, let's focus on having a great time here at Blah Bla X! Cheers!",
            "I get that. But let's not forget the main goal here — you having a fantastic time. Off you go!",
            "I see where you're coming from. Now, let's get back to the important thing — you enjoying your time here. Cheers!",
            "That's a valid point. But let's not forget the main reason you're here — to have fun! Now go enjoy yourself, the mirror will be here when you get back.",
        ])