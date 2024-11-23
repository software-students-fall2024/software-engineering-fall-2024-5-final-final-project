import nltk
import string
from nltk.stem import WordNetLemmatizer
from collections import defaultdict


def tokenize(text):
    """Tokenizes and lemmatizes the input text while filtering out stop words."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must be a non-empty string.")

    lemmatizer = WordNetLemmatizer()
    from nltk.corpus import stopwords
    try:
        stop_words = set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords")
        stop_words = set(stopwords.words("english"))

    # Tokenize, lemmatize, and filter stop words/punctuation
    tokens = nltk.word_tokenize(text.lower())
    return [
        lemmatizer.lemmatize(token.strip(string.punctuation))
        for token in tokens
        if token not in stop_words and token.isalpha()
    ]

def analyze_dream(dream_description):
    dream_symbols = {
        "falling": "Falling in a dream signifies insecurity, loss of control, or fear of failure. It may also reflect unresolved anxieties or the need to let go of burdens.",
        "flying": "Flying symbolizes freedom, ambition, or rising above challenges. Effortless flight suggests confidence, while struggling indicates self-doubt. The height and direction reflect aspirations and emotional state.",
        "water": "Water represents emotions and the subconscious. Calm water indicates peace, while rough water reflects turmoil. Being submerged suggests feeling overwhelmed, and crossing water symbolizes transitions or overcoming obstacles.",
        "teeth": "Teeth dreams relate to self-image, communication, or vulnerability. Losing teeth signifies anxiety, while healthy teeth reflect confidence. Broken teeth may indicate fear of judgment or insecurity.",
        "tooth": "Teeth dreams relate to self-image, communication, or vulnerability. Losing teeth signifies anxiety, while healthy teeth reflect confidence. Broken teeth may indicate fear of judgment or insecurity.",
        "chase": "Being chased symbolizes avoidance or pressure. An unknown pursuer reflects internal fears, while a known one highlights specific conflicts. Successfully escaping suggests overcoming challenges or resolving issues.",
        "death": "Death symbolizes transformation, endings, or change. Dreaming of your own death reflects fear or renewal, while another’s death suggests shifts in relationships or perspectives.",
        "animal": "Animals represent instincts, emotions, or traits. Dogs symbolize loyalty, cats suggest independence, and snakes indicate fear or transformation. Their behavior provides context for your emotional state.",
        "school": "Dreams about school reflect learning, growth, or performance anxiety. Being unprepared for tests indicates fear of failure. School settings highlight concerns about personal or professional development.",
        "money": "Money symbolizes self-worth, success, or insecurity. Finding money suggests confidence, losing it reflects scarcity fears, and spending indicates generosity. Hoarding money may symbolize fear of loss.",
        "darkness": "Darkness represents fear of the unknown, confusion, or introspection. Feeling lost suggests uncertainty, while finding light indicates hope or clarity about challenges in your waking life.",
        "light": "Light signifies clarity, hope, or enlightenment. Bright light suggests understanding or guidance, while dim light reflects doubt. Moving toward light symbolizes progress or overcoming challenges.",
        "door": "Doors symbolize opportunities or transitions. Open doors indicate new possibilities, while closed doors represent obstacles. Locked doors may reflect feeling blocked or unprepared for change.",
        "flight": "Flight represents a desire to overcome limitations or escape challenges. Flying freely indicates confidence, while struggling to fly suggests self-doubt or external restrictions in your waking life.",
        "tree": "Trees symbolize growth, stability, or life’s connections. Healthy trees reflect strength, while fallen ones suggest loss or instability. Branches may represent personal development or relationships.",
        "mirror": "Mirrors reflect self-perception, identity, or truth. Seeing your reflection may indicate self-awareness, while distorted reflections symbolize insecurity, deception, or distorted views of yourself or others.",
        "storm": "Storms represent emotional conflict or turmoil. Thunder or lightning may reflect sudden realizations, while clearing skies suggest resolution or relief after difficult situations.",
        "bird": "Birds symbolize freedom, hope, or spirituality. Flying birds reflect aspirations, while caged birds suggest feeling trapped. Specific birds, like doves, may indicate peace or harmony.",
        "fire": "Fire represents passion, transformation, or destructive energy. Controlled fire indicates renewal or ambition, while uncontrolled flames symbolize anger, chaos, or overwhelming emotions.",
        "baby": "Babies symbolize new beginnings, innocence, or potential. Caring for a baby may reflect nurturing a new project or aspect of yourself, while neglect suggests fear of responsibility.",
        "house": "Houses reflect your mind or self. Different rooms represent aspects of life—bedrooms signify intimacy, kitchens creativity, and basements subconscious thoughts. Damaged houses may indicate insecurity or emotional distress.",
        "stairs": "Stairs symbolize progress or challenges. Climbing stairs reflects ambition and success, while descending may indicate introspection or setbacks. Broken stairs suggest obstacles in achieving goals.",
        "key": "Keys represent access to opportunities or solutions. Finding keys indicates readiness, while losing them suggests insecurity or feeling blocked in achieving goals or understanding situations.",
        "bridge": "Bridges symbolize transitions, connections, or overcoming obstacles. Crossing a bridge represents progress, while a broken bridge suggests difficulty in moving forward or connecting different parts of life.",
        "mountain": "Mountains represent challenges, ambitions, or goals. Climbing a mountain symbolizes striving for success, while reaching the summit indicates achievement. Descending may reflect reflection or completion.",
        "clock": "Clocks symbolize awareness of time or urgency. A working clock reflects productivity, while a broken clock indicates feeling stuck, out of sync, or stressed about deadlines.",
        "eye": "Eyes represent insight, intuition, or observation. Clear vision reflects clarity and awareness, while blindness may indicate ignorance or a refusal to see the truth.",
        "road": "Roads symbolize life’s path. A clear road reflects progress, while forks indicate choices. Blocked or rough roads suggest obstacles or challenges in reaching your goals.",
        "rainbow": "A symbol of hope, promise, and optimism after a period of emotional or physical challenges. Rainbows often represent a bridge between difficult times and brighter days, and can signify divine blessings or resolution of inner conflict.",
        "shadow": "Hidden aspects of yourself, unacknowledged fears, or suppressed emotions coming to light. Dreaming of shadows may suggest a need to confront parts of your psyche you have been avoiding or ignoring.",
        "gold": "Symbolizes wealth, success, or personal value. Finding gold in a dream often represents uncovering inner talents or resources. It may also reflect greed or the pursuit of materialistic goals at the expense of emotional fulfillment.",
        "cave": "A representation of exploring your subconscious or facing hidden fears. Caves often indicate a retreat into the self for reflection and healing. Being lost in a cave may reflect confusion or feeling trapped in your thoughts.",
        "book": "Knowledge, learning, or the pursuit of wisdom. Books in dreams suggest seeking answers, gaining insights, or uncovering hidden truths. The content of the book, or being unable to read it, can provide further clues to its meaning.",
        "blood": "Represents life force, energy, or emotional pain. Blood in a dream can signify passion, vitality, or emotional wounds. Bleeding may symbolize feeling drained or giving too much of yourself to others.",
        "ring": "A sign of commitment, relationships, or cycles. A ring may represent unity and eternal bonds, particularly in romantic relationships. Losing a ring may indicate fear of commitment or concerns about trust and loyalty.",
        "boat": "Navigating emotions or life’s challenges. A boat floating on calm waters indicates peace and control, while one in turbulent waters reflects emotional struggles or uncertainty. The state of the boat reflects your ability to handle life’s ups and downs.",
        "candle": "Spirituality, hope, or the passage of time. A burning candle can represent clarity and guidance, while an extinguished one may suggest loss of hope or fear of the unknown. The brightness of the candle may mirror your optimism.",
        "rain": "A symbol of cleansing, renewal, or emotional release. Gentle rain may indicate healing and growth, while heavy rain can suggest overwhelming emotions or a need to release pent-up feelings.",
        "snow": "Purity, transformation, or isolation. Snow often represents a fresh start or a cooling of emotions. Being stuck in snow can indicate feeling frozen or stuck in a particular situation.",
        "desert": "Feeling lost, lonely, or in need of direction. A desert may represent emotional emptiness or a barren phase in your life. Finding water in a desert can symbolize hope or a hidden resource.",
        "jungle": "Exploring the unknown or chaos in your life. Jungles often represent the untamed aspects of your personality or the challenges you are currently facing. Finding a path in a jungle may symbolize discovering clarity amid confusion.",
        "flower": "Beauty, growth, or fleeting happiness. Different flowers carry unique meanings, such as roses symbolizing love, lilies representing purity, and daisies indicating innocence. Wilted flowers may suggest missed opportunities or fading hope.",
        "bee": "Hard work, productivity, or community. Bees in a dream may suggest the importance of teamwork or feeling overwhelmed by responsibilities. A bee sting could reflect a fear of criticism or being hurt emotionally.",
        "fish": "Subconscious thoughts, fertility, or spiritual insights. Seeing fish swimming freely may indicate emotional flow and abundance, while dead fish may suggest lost opportunities or suppressed feelings.",
        "shoe": "Your path in life or readiness for change. New shoes can symbolize a fresh start, while worn-out shoes suggest exhaustion or overburdened responsibilities. Losing a shoe may indicate insecurity or unpreparedness.",
        "tunnel": "Exploration, transformation, or a journey to the unknown. Passing through a tunnel can signify moving through a period of uncertainty or personal growth. The end of the tunnel often represents clarity or resolution.",
        "star": "Dreams, hopes, or guidance. Stars in a dream can reflect aspirations and inspiration. Falling stars may symbolize lost dreams or unfulfilled desires, while a constellation might represent a sense of connection to the universe.",
        "horse": "Freedom, power, or drive. A wild horse reflects untamed emotions or desires, while a calm horse may symbolize controlled strength. Riding a horse often indicates confidence or progress in life.",
        "mask": "Hidden identities, secrets, or deception. Wearing a mask in a dream may indicate feelings of insecurity or a need to hide your true self. Seeing others in masks may suggest mistrust or concern about authenticity.",
        "lock": "Protection, privacy, or feeling stuck. A locked door may symbolize barriers to opportunities, while unlocking a door can represent solving a problem or uncovering a hidden truth.",
        "box": "Secrets, surprises, or potential. An open box may indicate discovery, while a sealed box represents something hidden or protected. The contents of the box often provide further insight into the dream’s meaning.",
        "train": "Life’s journey, direction, or a sense of purpose. Missing a train may indicate missed opportunities or feeling left behind. Being on the wrong train suggests uncertainty about your life’s path.",
        "spider": "Creativity, patience, or feeling trapped. Spiders weaving a web can symbolize building connections or being caught in a complex situation. Fear of spiders may reflect anxiety about manipulation or vulnerability.",
        "butterfly": "Transformation, growth, or beauty. A butterfly often symbolizes personal evolution or fleeting moments of joy. Catching a butterfly may represent trying to hold onto something ephemeral.",
        "frog": "Adaptation, cleansing, or change. Frogs in dreams can symbolize renewal or emotional cleansing. A jumping frog may reflect a need to take a leap of faith or adapt to a new situation.",
        "cat": "Mystery, independence, or feminine energy. A friendly cat may symbolize intuition or nurturing qualities, while an aggressive cat might indicate repressed emotions or concerns about deceit.",
        "ladder": "Progress, growth, or reaching goals. Climbing a ladder indicates ambition and success, while descending may symbolize reflection or setbacks. A broken ladder can represent obstacles or difficulties in achieving your objectives.",
        "rock": "Stability, obstacles, or strength. Rocks in a dream can signify resilience and enduring challenges. Climbing rocks may indicate overcoming obstacles, while being stuck among rocks may symbolize feeling trapped.",
        "wind": "Change, freedom, or unseen forces. A gentle breeze may represent peace and harmony, while strong winds can symbolize tumultuous changes or external pressures. The direction of the wind may indicate the flow of your life.",
        "destruction": "Change, letting go, or fear of loss. Destruction in a dream may indicate the end of something to make way for new beginnings. Watching destruction may reflect fear or resistance to inevitable change.",
        "island": "Isolation, independence, or self-reflection. Being alone on an island can indicate a need for solitude or feelings of abandonment. A lush island represents abundance, while a barren one suggests loneliness or lack.",
        "firework": "Celebration, creativity, or emotional outbursts. Fireworks in dreams often symbolize a release of repressed feelings or a need for recognition and excitement. The colors and patterns may reflect your current emotions.",
        "broken": "Fragility, shattered expectations, or loss. Broken glass may indicate vulnerability or a sense of something precious being damaged. Walking on broken glass could symbolize enduring pain or obstacles.",
        "ocean": "Depth of emotions, vast possibilities, or subconscious exploration. Calm oceans signify peace and stability, while turbulent oceans reflect overwhelming emotions or unresolved conflicts.",
        "chair": "Stability, rest, or waiting. An empty chair may suggest absence or longing for someone, while sitting in a chair symbolizes contentment or a need for a pause.",
        "forest": "Forests symbolize exploration, mystery, or personal growth. Being lost reflects confusion, while navigating successfully suggests self-discovery. A dense forest may represent untapped potential or hidden challenges.",
        "weapon": "Weapons symbolize conflict, self-defense, or aggression. Wielding one suggests asserting power, while being attacked reflects vulnerability or fear of confrontation. Broken weapons indicate resolving conflicts.",
        "hat": "Hats symbolize roles, identity, or concealment. Wearing a hat may indicate adopting a new role, while removing it reflects openness or shedding a facade.",
        "cooking": "Cooking symbolizes nurturing, creativity, or transformation. Preparing food represents growth or caring for others, while burning food suggests anxiety about meeting expectations.",
        "hand": "Hands symbolize action, connection, or creativity. Holding hands reflects relationships, while injured hands suggest difficulty expressing yourself or achieving goals.",
        "sky": "Skies represent freedom, ambition, or limitless possibilities. Clear skies suggest optimism, while stormy skies reflect challenges. Night skies may indicate introspection or hidden potential.",
        "chain": "Chains symbolize restriction, attachment, or feeling trapped. Breaking chains reflects freedom or overcoming limitations, while being bound by them suggests unresolved obligations or fears.",
        "paper": "Paper represents communication, creativity, or potential. Writing on paper suggests self-expression, while blank paper indicates opportunity. Torn paper may symbolize lost connections or unfinished business.",
        "tiger": "Tigers symbolize courage, strength, or danger. Facing a tiger reflects confronting fears, while being attacked indicates feeling threatened. A calm tiger represents harnessed power or control.",
        "wolve": "Wolves symbolize instinct, protection, or fear. A lone wolf reflects independence, while a pack suggests community. Being pursued by wolves indicates anxiety or unresolved conflict.",
        "umbrella": "Umbrellas symbolize protection, preparation, or hidden feelings. An open umbrella suggests readiness for challenges, while a broken one reflects feeling vulnerable or unprepared.",
        "fruit": "Fruit symbolizes abundance, growth, or desire. Ripe fruit reflects success and fulfillment, while spoiled fruit suggests missed opportunities or unfulfilled potential.",
        "car": "Cars symbolize control, direction, or independence. Driving confidently indicates control over your path, while losing control suggests uncertainty. Being a passenger may reflect dependency or lack of autonomy.",
        "path": "Paths symbolize choices, direction, or new opportunities. A clear path reflects confidence, while a fork indicates decisions. A blocked path may suggest obstacles or uncertainty.",
        "volcano": "Volcanoes represent repressed anger, emotions, or transformation. An erupting volcano suggests emotional outbursts or sudden change, while a dormant one reflects hidden feelings or potential.",
        "lake": "Lakes symbolize calm emotions or introspection. Clear lakes reflect peace and clarity, while murky lakes indicate emotional uncertainty or unresolved feelings.",
        "wave": "Waves represent overwhelming emotions or external pressures. Gentle waves suggest manageable challenges, while crashing waves reflect being overcome by powerful feelings or chaotic situations.",
        "snowflake": "Snowflakes symbolize uniqueness, delicacy, or fleeting moments. Catching snowflakes reflects appreciating life's beauty, while melting snowflakes may indicate the transience of an opportunity or experience.",
        "pearl": "Pearls represent hidden potential, purity, or uniqueness. Finding a pearl signifies uncovering inner beauty or talents, while losing one may reflect self-doubt or missed opportunities.",
        "pillar": "Pillars symbolize strength, support, or foundations. Strong pillars reflect stability and reliability, while crumbling pillars may suggest insecurity or a weakening of core beliefs.",
        "puzzle": "Puzzles symbolize complexity, challenges, or problem-solving. Completing a puzzle reflects resolving issues, while missing pieces suggest feeling incomplete or lacking clarity.",
        "raindrop": "Raindrops symbolize cleansing, renewal, or emotional release. Gentle raindrops reflect healing and growth, while heavy rain suggests the need to process and release deep emotions.",
        "scale": "Scales symbolize balance, justice, or decision-making. Balanced scales reflect fairness or harmony, while uneven scales suggest inner conflict or unresolved decisions.",
        "skeleton": "Skeletons symbolize mortality, hidden truths, or the past. Seeing skeletons may reflect fears of vulnerability, uncovering secrets, or revisiting unresolved memories.",
        "smoke": "Smoke symbolizes confusion, illusion, or hidden dangers. Thick smoke reflects obscured truth or doubt, while clearing smoke suggests gaining clarity or escaping uncertainty.",
        "snake": "Snakes symbolize fear, transformation, or hidden threats. A threatening snake reflects anxieties, while shedding skin suggests personal growth or leaving old habits behind.",
        "sun": "The sun represents life, energy, or consciousness. A bright sun reflects positivity and renewal, while an obscured sun suggests doubt or challenges in finding clarity.",
        "sword": "Swords symbolize conflict, power, or protection. Wielding a sword reflects asserting authority, while being threatened by one suggests vulnerability or fear of confrontation.",
        "thorn": "Thorns symbolize pain, protection, or defense. Encountering thorns reflects challenges or emotional wounds, while removing them suggests healing or resolving conflicts.",
        "balloon": "Balloons symbolize celebration, joy, or letting go. Releasing balloons reflects freedom or emotional release, while bursting balloons suggest dashed hopes or unexpected disappointment.",
        "cage": "Cages symbolize feeling trapped or restricted. Being inside reflects limitations or confinement, while escaping suggests breaking free from obstacles or emotional constraints.",
        "cliff": "Cliffs symbolize taking risks or facing fears. Standing on a cliff reflects decision-making or fear of failure, while falling suggests insecurity or lack of control.",
        "cloud": "Clouds symbolize confusion, thoughts, or temporary obstacles. Clear clouds reflect optimism, while dark clouds suggest looming challenges or emotional heaviness.",
        "crystal": "Crystals symbolize clarity, healing, or spiritual growth. Clear crystals reflect insight and purity, while shattered ones suggest broken trust or unresolved issues.",
        "diamond": "Diamonds symbolize value, strength, or clarity. Finding a diamond reflects recognizing inner worth, while losing one suggests insecurity or undervaluing yourself.",
        "dragon": "Dragons symbolize power, strength, or hidden fears. A friendly dragon reflects inner confidence, while a threatening one suggests unresolved fears or challenges.",
        "egg": "Eggs symbolize potential, new beginnings, or fragility. Cracking an egg reflects personal growth, while breaking one unintentionally suggests fear of damaging something valuable.",
        "feather": "Feathers symbolize lightness, freedom, or spirituality. Catching feathers reflects hope or inspiration, while losing them suggests feeling burdened or disconnected from your goals.",
        "garden": "Gardens symbolize growth, peace, or nurturing. A blooming garden reflects personal growth, while a neglected one suggests feelings of stagnation or neglecting self-care.",
        "gate": "Gates symbolize opportunities, transitions, or barriers. Open gates reflect new possibilities, while closed gates suggest obstacles. Passing through a gate represents moving into a new phase of life.",
        "ghost": "Ghosts represent past issues, fears, or unresolved emotions. Seeing a ghost suggests lingering memories or regrets, while confronting one reflects a desire to move on from the past.",
        "glove": "Gloves symbolize protection, preparation, or concealment. Wearing gloves reflects readiness for challenges or hiding true intentions, while removing gloves suggests openness or vulnerability.",
        "honey": "Honey symbolizes sweetness, reward, or hard work. Tasting honey reflects enjoying the fruits of labor, while spilling it suggests missing out on opportunities or feeling unappreciated.",
        "ice": "Ice represents emotional coldness, stagnation, or clarity. Walking on ice reflects risk, while melting ice suggests emotional thawing or overcoming obstacles.",
        "jewel": "Jewels symbolize value, beauty, or personal worth. Finding jewels reflects discovering inner potential, while losing them suggests insecurity or undervaluing yourself.",
        "labyrinth": "Labyrinths symbolize complexity, confusion, or a journey. Navigating one reflects problem-solving, while being lost suggests feeling overwhelmed by life’s challenges.",
        "lantern": "Lanterns symbolize guidance, hope, or enlightenment. A bright lantern reflects clarity or support, while a dim one suggests uncertainty or dwindling inspiration.",
        "leave": "Leaves symbolize change, growth, or time passing. Falling leaves reflect transitions or endings, while green leaves indicate renewal or fresh starts.",
        "lightning": "Lightning represents sudden insight, power, or destruction. Seeing lightning reflects unexpected clarity or energy, while being struck suggests a shocking revelation or emotional impact.",
        "lion": "Lions symbolize courage, strength, or leadership. A calm lion reflects confidence, while an aggressive one suggests suppressed anger or challenges to authority.",
        "moon": "Moons represent intuition, emotions, or cycles. A full moon reflects completion or heightened awareness, while a new moon suggests fresh beginnings or hidden potential.",
        "mushroom": "Mushrooms symbolize growth, transformation, or hidden potential. Seeing mushrooms reflects personal development, while poisonous ones suggest caution about hidden dangers.",
        "net": "Nets symbolize feeling trapped, connections, or capturing opportunities. Escaping a net reflects freedom, while being caught suggests entanglement in challenging situations.",
        "owl": "Owls symbolize wisdom, intuition, or secrets. Seeing an owl reflects gaining insight or discovering hidden truths, while a silent owl suggests a need for introspection.",
        "phoenix": "Phoenixes symbolize rebirth, transformation, or renewal. Seeing a phoenix reflects overcoming difficulties or starting anew after a significant change.",
        "piano": "Pianos symbolize creativity, harmony, or emotional expression. Playing a piano reflects emotional release, while a broken piano suggests difficulties expressing feelings or achieving balance.",
        "pillow": "Pillows symbolize rest, comfort, or dreams. A soft pillow reflects peace and relaxation, while a damaged one suggests discomfort or disturbed rest.",
        "rose": "Roses symbolize love, beauty, or passion. A blooming rose reflects affection or success, while wilted roses suggest lost opportunities or fading emotions.",
        "sand": "Sand symbolizes time, impermanence, or instability. Walking on sand reflects uncertainty, while sand slipping through fingers suggests fleeting opportunities or passing time.",
        "scissor": "Scissors symbolize separation, cutting ties, or precision. Using scissors reflects decisiveness, while broken scissors suggest difficulty making decisions or resolving conflicts.",
        "shell": "Shells symbolize protection, secrets, or the subconscious. Finding a shell reflects self-discovery, while a broken shell suggests vulnerability or loss of security.",
        "ship": "Ships symbolize journeys, exploration, or navigating emotions. A smooth voyage reflects progress, while a sinking ship suggests fear of failure or emotional overwhelm.",
        "spark": "Sparks symbolize inspiration, creativity, or potential. Seeing sparks reflects new ideas or energy, while extinguished sparks suggest lost motivation or missed opportunities.",
        "suitcase": "Suitcases symbolize preparation, travel, or emotional baggage. Packing a suitcase reflects readiness for change, while unpacking suggests resolving past issues or adapting to new circumstances.",
        "swing": "Swings symbolize childhood, playfulness, or ups and downs. Swinging freely reflects joy or nostalgia, while falling off a swing suggests instability or loss of balance.",
        "telescope": "Telescopes symbolize vision, future, or exploration. Using a telescope reflects seeking clarity or long-term goals, while a broken one suggests difficulty understanding or planning for the future.",
        "thunder": "Thunder represents power, anger, or sudden change. Hearing thunder reflects emotional intensity or a dramatic event, while distant thunder suggests looming challenges or conflicts.",
        "tide": "Tides symbolize emotional ebb and flow, cycles, or change. Rising tides reflect overwhelming emotions, while receding tides suggest resolution or a temporary pause in challenges.",
        "tower": "Towers symbolize isolation, protection, or ambition. Climbing a tower reflects striving for success, while being trapped in one suggests feeling confined or disconnected from others.",
        "treasure": "Treasure symbolizes hidden talents, rewards, or self-discovery. Finding treasure reflects uncovering personal value, while losing it suggests insecurity or fear of missing opportunities.",
        "vines": "Vines symbolize growth, entanglement, or connections. Thriving vines reflect progress and relationships, while tangled ones suggest complications or feeling stuck in certain situations.",
        "wheels": "Wheels symbolize cycles, progress, or movement. Turning wheels reflect forward motion, while broken wheels suggest obstacles or delays in achieving your goals.",
        "window": "Windows symbolize opportunities, perspectives, or clarity. Looking through a window reflects seeking understanding, while a closed window suggests missed opportunities or limited insight.",
        "wing": "Wings symbolize freedom, spirituality, or aspirations. Spreading wings reflects achieving independence, while damaged wings suggest feeling held back or unable to pursue your dreams.",
        "wire": "Wires symbolize connections, communication, or constraints. Tangled wires reflect miscommunication or complexity, while clear wires suggest strong connections or efficient interaction.",
        "wreath": "Wreaths symbolize completion, unity, or celebration. A fresh wreath reflects harmony and success, while a withered wreath suggests ending or loss of fulfillment.",
        "zebra": "Zebras symbolize balance, individuality, or blending in. Seeing a zebra reflects navigating dualities, while interacting with one suggests embracing unique traits or finding harmony in contrasts.",
        "zodiac": "The zodiac symbolizes destiny, personality, or cosmic forces. Observing zodiac signs reflects self-discovery or spiritual alignment, while confusion with them suggests uncertainty about life’s direction.",
        "zoo": "Zoos symbolize control, confinement, or exploring aspects of yourself. Watching animals reflects self-exploration, while feeling trapped in a zoo suggests restrictions or a need for freedom.",
        "avalanche": "Avalanches symbolize overwhelming emotions or events. Being caught reflects feeling buried by responsibilities, while watching one suggests fear of losing control or sudden, dramatic changes.",
        "backpack": "Backpacks symbolize burdens, responsibilities, or preparedness. Carrying one suggests handling obligations, while a heavy backpack reflects feeling overwhelmed. An empty backpack may indicate readiness for a fresh start.",
        "barn": "Barns symbolize storage, abundance, or nurturing. A full barn reflects prosperity and resourcefulness, while an empty one suggests lack or missed opportunities.",
        "bicycle": "Bicycles symbolize balance, independence, or progress. Riding confidently suggests control, while struggling reflects difficulties in maintaining balance or navigating challenges.",
        "binocular": "Binoculars symbolize foresight, observation, or focus. Using binoculars suggests looking ahead or seeking clarity, while broken binoculars indicate difficulty in seeing the bigger picture.",
        "blanket": "Blankets symbolize comfort, protection, or security. Wrapping yourself in a blanket reflects self-care, while losing one suggests vulnerability or lack of emotional support.",
        "broom": "Brooms symbolize cleaning, renewal, or removing negativity. Sweeping reflects clearing out old habits or emotions, while a broken broom suggests difficulty letting go.",
        "cactus": "Cacti symbolize resilience, endurance, or emotional defenses. Thriving cacti reflect strength, while touching their thorns suggests dealing with painful or protective boundaries.",
        "calendar": "Calendars symbolize time, planning, or deadlines. A marked calendar reflects preparedness, while an empty one suggests uncertainty or a need to organize priorities.",
        "camera": "Cameras symbolize memories, perspective, or self-reflection. Taking pictures reflects preserving moments, while a broken camera suggests difficulty in capturing or understanding your experiences.",
        "canoe": "Canoes symbolize navigating emotions or personal journeys. A smooth ride reflects balance, while rough waters suggest struggles or challenges in moving forward.",
        "castle": "Castles symbolize ambition, security, or isolation. Living in a castle reflects power or self-protection, while being locked out suggests feeling excluded or unworthy.",
        "chandelier": "Chandeliers symbolize elegance, illumination, or aspirations. A glowing chandelier reflects clarity or inspiration, while a broken one suggests lost prestige or dimmed hopes.",
        "chessboard": "Chessboards symbolize strategy, decisions, or conflicts. Playing suggests careful planning, while an unfinished game reflects unresolved issues or uncertainty.",
        "clocktower": "Clocktowers symbolize time, urgency, or awareness. Seeing a clocktower reflects responsibility or timing, while a stopped clocktower suggests feeling stuck or out of sync.",
        "comet": "Comets symbolize fleeting opportunities, wonder, or sudden changes. Seeing a comet reflects awe or rare chances, while missing one suggests regret or inattention.",
        "compass": "Compasses symbolize direction, guidance, or purpose. A working compass reflects clarity in life’s path, while a broken one suggests confusion or feeling lost.",
        "coral": "Corals symbolize beauty, resilience, or community. Thriving coral reflects emotional support and growth, while damaged coral suggests neglect or lost connections.",
        "crown": "Crowns symbolize authority, achievement, or recognition. Wearing a crown reflects confidence and leadership, while losing one suggests insecurity or fear of losing status.",
        "dam": "Dams symbolize control, restraint, or emotional barriers. A strong dam reflects control over emotions, while a broken dam suggests overwhelming feelings or loss of control.",
        "eclipse": "Eclipses symbolize temporary obscurity, transitions, or revelations. Witnessing an eclipse reflects change or hidden truths, while being afraid suggests fear of the unknown.",
        "elevator": "Elevators symbolize progress, transitions, or direction. Moving up reflects success, while descending suggests introspection or setbacks. A stuck elevator reflects feeling trapped or stagnant.",
        "fence": "Fences symbolize boundaries, protection, or obstacles. Climbing a fence reflects overcoming challenges, while being blocked by one suggests feeling restricted.",
        "fountain": "Fountains symbolize abundance, renewal, or emotional release. A flowing fountain reflects vitality, while a dry one suggests stagnation or emotional depletion.",
        "galaxy": "Galaxies symbolize vast possibilities, wonder, or exploration. Viewing a galaxy reflects awe of the unknown, while feeling lost in one suggests being overwhelmed by life’s complexity.",
        "hammock": "Hammocks symbolize rest, relaxation, or escapism. Lying in a hammock reflects peace, while falling from one suggests difficulty finding balance or comfort.",
        "harp": "Harps symbolize harmony, spirituality, or emotional expression. Hearing harp music reflects peace, while broken strings suggest discord or emotional struggles.",
        "igloo": "Igloos symbolize shelter, adaptation, or emotional detachment. Living in an igloo reflects resilience in harsh conditions, while feeling cold suggests emotional isolation.",
        "kite": "Kites symbolize freedom, aspirations, or connection. Flying a kite reflects achieving goals, while a falling kite suggests setbacks or loss of direction.",
        "lighthouse": "Lighthouses symbolize guidance, hope, or warnings. Seeing a lighthouse reflects seeking clarity or safety, while a dark lighthouse suggests losing direction or ignoring signs.",
        "magnet": "Magnets symbolize attraction, influence, or connection. Being drawn to something reflects curiosity or relationships, while repulsion suggests avoiding situations or conflicts.",
        "maze": "Mazes symbolize complexity, confusion, or personal growth. Navigating a maze reflects problem-solving, while feeling lost suggests uncertainty or being overwhelmed by challenges.",
        "meteor": "Meteors symbolize sudden events, inspiration, or fleeting moments. Seeing a meteor reflects awe or opportunities, while missing one suggests regret or inattention.",
        "microscope": "Microscopes symbolize attention to detail, analysis, or introspection. Using one reflects examining aspects of your life, while a broken microscope suggests difficulty understanding something important.",
        "nest": "Nests symbolize home, security, or nurturing. A full nest reflects stability, while an empty nest suggests change, loss, or transition.",
        "orchard": "Orchards symbolize abundance, growth, or rewards. A thriving orchard reflects prosperity, while a neglected one suggests stagnation or missed opportunities.",
        "palace": "Palaces symbolize luxury, ambition, or self-worth. Living in a palace reflects confidence, while feeling out of place suggests insecurity or self-doubt.",
        "parachute": "Parachutes symbolize safety, preparation, or controlled descent. Using a parachute reflects managing risks, while a failing parachute suggests fear of failure or lack of security.",
        "planet": "Planets symbolize exploration, vastness, or life’s cycles. Seeing planets reflects wonder and curiosity, while a distant planet suggests feeling isolated or disconnected.",
        "raft": "Rafts symbolize survival, resourcefulness, or emotional support. Floating on a raft reflects navigating challenges, while a sinking raft suggests feeling overwhelmed or unprepared.",
        "reef": "Reefs symbolize protection, hidden dangers, or community. Thriving reefs reflect emotional support, while damaged reefs suggest neglected relationships or unseen challenges.",
        "rocket": "Rockets symbolize ambition, progress, or rapid change. Launching a rocket reflects striving for goals, while a failed launch suggests setbacks or disappointment.",
        "satellite": "Satellites symbolize communication, observation, or dependency. Seeing one reflects seeking connection or insight, while losing contact suggests feeling isolated or out of touch.",
        "sculpture": "Sculptures symbolize creativity, permanence, or self-expression. Creating a sculpture reflects showcasing talents, while a broken one suggests lost inspiration or damaged self-image.",
        "skyscraper": "Skyscrapers symbolize ambition, success, or perspective. Reaching the top reflects achievement, while falling from one suggests fear of failure or losing status.",
        "sled": "Sleds symbolize fun, nostalgia, or control. Sledding downhill reflects ease in life’s path, while struggling uphill suggests facing challenges.",
        "submarine": "Submarines symbolize exploration, introspection, or hidden emotions. Diving underwater reflects delving into the subconscious, while being stuck suggests difficulty confronting deep feelings.",
        "temple": "Temples symbolize spirituality, reflection, or sacredness. Visiting a temple reflects seeking peace or higher purpose, while a damaged temple suggests spiritual conflict or lost faith.",
        "tent": "Tents symbolize temporary shelter, adaptability, or impermanence. Living in a tent reflects flexibility, while a collapsed tent suggests instability or lack of support."
    }

    try:
        # Preprocess the input text
        preprocessed_words = tokenize(dream_description)

        # Analyze for matching symbols
        analysis = defaultdict(list)
        for word in preprocessed_words:
            if word in dream_symbols:
                analysis["symbols"].append(word)
                analysis["interpretations"].append(dream_symbols[word])

        # Formulate the result
        if analysis["symbols"]:
            result = f"Dream Analysis:\n\nDream Description: {dream_description}\n\n"
            result += "Identified Symbols:\n"
            for symbol, interpretation in zip(analysis["symbols"], analysis["interpretations"]):
                result += f"- {symbol.capitalize()}: {interpretation}\n"
            return result
        else:
            return "No specific symbols were identified in your dream. Try describing it in more detail!"

    except Exception as e:
        return f"An error occurred during analysis: {str(e)}"

# Example usage:
if __name__ == "__main__":
    nltk.download("punkt")  # Ensure the required NLTK resources are downloaded
    nltk.download("stopwords")
    nltk.download("wordnet")

    dream = "I was falling in a dark forest, chased by an animal."
    print(analyze_dream(dream))