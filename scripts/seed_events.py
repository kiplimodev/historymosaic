# scripts/seed_events.py
# Generates the curated historical events library.
# Run from project root: python -m scripts.seed_events

import json
from pathlib import Path

EVENTS_DIR = Path("events")
EVENTS_DIR.mkdir(exist_ok=True)

EVENTS = [
    {
        "title": "Assassination of Julius Caesar",
        "date": "0044-03-15",
        "summary": (
            "On March 15, 44 BC — the Ides of March — Roman dictator Julius Caesar was "
            "stabbed 23 times on the floor of the Roman Senate by a group of senators led "
            "by Brutus and Cassius. His assassination triggered a series of civil wars that "
            "ultimately ended the Roman Republic and gave rise to the Roman Empire under his "
            "adopted heir, Octavian (Augustus)."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Assassination_of_Julius_Caesar"],
    },
    {
        "title": "Fall of the Western Roman Empire",
        "date": "0476-09-04",
        "summary": (
            "On September 4, 476 AD, the Germanic chieftain Odoacer deposed Romulus Augustulus, "
            "the last emperor of the Western Roman Empire, marking the traditional end of ancient "
            "Rome in the West. This date is widely used by historians as the boundary between "
            "classical antiquity and the Middle Ages, reshaping the course of European civilization."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Fall_of_the_Western_Roman_Empire"],
    },
    {
        "title": "Battle of Hastings",
        "date": "1066-10-14",
        "summary": (
            "On October 14, 1066, William the Conqueror of Normandy defeated King Harold II of "
            "England at the Battle of Hastings, one of the most decisive battles in English history. "
            "Harold was killed — reportedly by an arrow to the eye — and William became King of "
            "England, permanently transforming English language, culture, and governance through "
            "Norman influence."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Battle_of_Hastings"],
    },
    {
        "title": "Magna Carta Signed",
        "date": "1215-06-15",
        "summary": (
            "On June 15, 1215, King John of England was forced by rebellious barons to seal the "
            "Magna Carta at Runnymede. The document established for the first time that the king "
            "was subject to the rule of law and guaranteed certain legal rights to free men. It "
            "became the foundation of constitutional governance, inspiring democratic frameworks "
            "across the world for centuries."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Magna_Carta"],
    },
    {
        "title": "Black Death Reaches Europe",
        "date": "1347-10-01",
        "summary": (
            "In October 1347, twelve Genoese trading ships docked at the Sicilian port of Messina "
            "carrying sailors dying of a mysterious illness — the Black Death. Over the next five "
            "years, the bubonic plague swept across Europe, killing an estimated 30–60% of the "
            "continent's population. It was the deadliest pandemic in human history and permanently "
            "altered European society, economics, and religion."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Black_Death"],
    },
    {
        "title": "Fall of Constantinople",
        "date": "1453-05-29",
        "summary": (
            "On May 29, 1453, Ottoman Sultan Mehmed II conquered Constantinople, the capital of "
            "the Byzantine Empire, after a 53-day siege. The fall ended the thousand-year Byzantine "
            "Empire and marked a turning point between the Middle Ages and the modern era. It "
            "accelerated the flow of Greek scholars and texts into Western Europe, contributing "
            "to the Renaissance."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Fall_of_Constantinople"],
    },
    {
        "title": "Columbus Reaches the Americas",
        "date": "1492-10-12",
        "summary": (
            "On October 12, 1492, Christopher Columbus, sailing under the Spanish crown, made "
            "landfall in the Bahamas, becoming the first European to reach the Americas in the "
            "modern era. The voyage initiated sustained contact between Europe and the Americas, "
            "setting off the Columbian Exchange — a massive transfer of plants, animals, culture, "
            "and disease that permanently transformed both worlds."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Voyages_of_Christopher_Columbus"],
    },
    {
        "title": "Martin Luther Posts 95 Theses",
        "date": "1517-10-31",
        "summary": (
            "On October 31, 1517, German monk Martin Luther nailed his 95 Theses to the door of "
            "the Castle Church in Wittenberg, challenging the Catholic Church's practice of selling "
            "indulgences. His act ignited the Protestant Reformation, fracturing Western Christianity "
            "and reshaping European politics, culture, and the relationship between individuals "
            "and religious authority for centuries."
        ),
        "sources": ["https://en.wikipedia.org/wiki/The_Ninety-five_Theses"],
    },
    {
        "title": "Newton Publishes Principia Mathematica",
        "date": "1687-07-05",
        "summary": (
            "On July 5, 1687, Isaac Newton published Philosophiæ Naturalis Principia Mathematica, "
            "laying the foundations for classical mechanics. The work introduced Newton's three laws "
            "of motion and the law of universal gravitation, unifying terrestrial and celestial "
            "physics for the first time. It is widely regarded as one of the most important "
            "scientific works ever written."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Philosophi%C3%A6_Naturalis_Principia_Mathematica"],
    },
    {
        "title": "American Declaration of Independence",
        "date": "1776-07-04",
        "summary": (
            "On July 4, 1776, the Continental Congress adopted the Declaration of Independence, "
            "proclaiming the thirteen American colonies free from British rule. Drafted primarily "
            "by Thomas Jefferson, the document declared that all men are created equal and endowed "
            "with unalienable rights. It inspired independence and democratic movements around "
            "the world for generations."
        ),
        "sources": ["https://en.wikipedia.org/wiki/United_States_Declaration_of_Independence"],
    },
    {
        "title": "Storming of the Bastille",
        "date": "1789-07-14",
        "summary": (
            "On July 14, 1789, Parisian revolutionaries stormed the Bastille fortress-prison, "
            "a symbol of royal tyranny, marking the violent start of the French Revolution. "
            "The event overthrew the Ancien Régime and spread the ideals of liberty, equality, "
            "and fraternity across Europe and beyond. July 14 remains France's national holiday, "
            "Bastille Day, to this day."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Storming_of_the_Bastille"],
    },
    {
        "title": "Napoleon Crowned Emperor",
        "date": "1804-12-02",
        "summary": (
            "On December 2, 1804, Napoleon Bonaparte was crowned Emperor of the French at "
            "Notre-Dame Cathedral in Paris, in a ceremony attended by Pope Pius VII. In a "
            "defining act of defiance, Napoleon took the crown from the Pope and placed it "
            "on his own head. The coronation marked the peak of his power and signaled the "
            "transformation of revolutionary France into an imperial European superpower."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Coronation_of_Napoleon_I"],
    },
    {
        "title": "Abolition of the Slave Trade",
        "date": "1807-03-25",
        "summary": (
            "On March 25, 1807, the British Parliament passed the Slave Trade Act, abolishing "
            "the transatlantic slave trade across the British Empire. The act was the result of "
            "decades of campaigning by abolitionists including William Wilberforce and formerly "
            "enslaved people like Olaudah Equiano. It was a landmark moment in the long struggle "
            "for human freedom, though slavery itself in British colonies was not abolished "
            "until 1833."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Slave_Trade_Act_1807"],
    },
    {
        "title": "Darwin Publishes Origin of Species",
        "date": "1859-11-24",
        "summary": (
            "On November 24, 1859, Charles Darwin published On the Origin of Species, introducing "
            "the scientific theory of evolution by natural selection. The book presented evidence "
            "that all species of life descended from common ancestors through a process of gradual "
            "change. It fundamentally transformed biology, challenged religious orthodoxy, and "
            "remains one of the most influential scientific texts in history."
        ),
        "sources": ["https://en.wikipedia.org/wiki/On_the_Origin_of_Species"],
    },
    {
        "title": "End of the American Civil War",
        "date": "1865-04-09",
        "summary": (
            "On April 9, 1865, Confederate General Robert E. Lee surrendered to Union General "
            "Ulysses S. Grant at Appomattox Court House in Virginia, effectively ending the "
            "American Civil War. The four-year conflict had claimed over 620,000 lives and settled "
            "the questions of secession and slavery. The Union's victory preserved the United "
            "States and led to the abolition of slavery through the 13th Amendment."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Appomattox_Court_House_National_Historical_Park"],
    },
    {
        "title": "Edison Demonstrates the Light Bulb",
        "date": "1879-12-31",
        "summary": (
            "On December 31, 1879, Thomas Edison gave the first public demonstration of his "
            "incandescent light bulb in Menlo Park, New Jersey, lighting the street for a crowd "
            "of visitors. The practical electric light bulb transformed human civilization, "
            "extending productive hours beyond sunset and laying the groundwork for the modern "
            "electrical grid and industrialized society."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Incandescent_light_bulb"],
    },
    {
        "title": "Wright Brothers First Flight",
        "date": "1903-12-17",
        "summary": (
            "On December 17, 1903, Orville and Wilbur Wright achieved the first successful "
            "powered, controlled airplane flight near Kitty Hawk, North Carolina. Orville piloted "
            "the first flight, lasting 12 seconds and covering 120 feet. The achievement launched "
            "the aviation age, compressing global distances and transforming warfare, commerce, "
            "and human exploration within a single generation."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Wright_brothers_in_history"],
    },
    {
        "title": "Titanic Sinks in the Atlantic",
        "date": "1912-04-15",
        "summary": (
            "In the early hours of April 15, 1912, the RMS Titanic sank in the North Atlantic "
            "after striking an iceberg on her maiden voyage from Southampton to New York. Over "
            "1,500 of the 2,224 passengers and crew perished, making it one of the deadliest "
            "peacetime maritime disasters in history. The tragedy led to sweeping reforms in "
            "maritime safety regulations worldwide."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Sinking_of_the_Titanic"],
    },
    {
        "title": "Assassination of Archduke Franz Ferdinand",
        "date": "1914-06-28",
        "summary": (
            "On June 28, 1914, Archduke Franz Ferdinand, heir to the Austro-Hungarian throne, "
            "was assassinated in Sarajevo by Gavrilo Princip, a Bosnian-Serb nationalist. "
            "The killing set off a chain of diplomatic failures and alliance obligations that "
            "plunged Europe into World War I within weeks, a conflict that killed over 17 million "
            "people and reshaped the world's political map."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Assassination_of_Archduke_Franz_Ferdinand"],
    },
    {
        "title": "Russian Bolshevik Revolution",
        "date": "1917-11-07",
        "summary": (
            "On November 7, 1917, Vladimir Lenin's Bolshevik Party seized power in Petrograd, "
            "overthrowing the Russian Provisional Government in what became known as the October "
            "Revolution. The coup ended centuries of Romanov rule and established the world's "
            "first communist state. The Soviet Union that followed shaped global politics, "
            "ideology, and the Cold War for the next seven decades."
        ),
        "sources": ["https://en.wikipedia.org/wiki/October_Revolution"],
    },
    {
        "title": "World War I Armistice Signed",
        "date": "1918-11-11",
        "summary": (
            "At 11 AM on November 11, 1918 — the eleventh hour of the eleventh day of the "
            "eleventh month — the armistice ending World War I came into effect. After four "
            "years of devastating trench warfare that killed over 17 million people, the guns "
            "fell silent on the Western Front. The armistice ended the Great War but planted "
            "seeds of resentment that would lead to World War II two decades later."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Armistice_of_11_November_1918"],
    },
    {
        "title": "Fleming Discovers Penicillin",
        "date": "1928-09-28",
        "summary": (
            "On September 28, 1928, Scottish bacteriologist Alexander Fleming returned to his "
            "laboratory to discover that mold — Penicillium notatum — had contaminated a petri "
            "dish and was killing the surrounding bacteria. This accidental discovery led to the "
            "development of penicillin, the world's first antibiotic. It is estimated to have "
            "saved over 200 million lives since its widespread introduction in the 1940s."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Alexander_Fleming"],
    },
    {
        "title": "D-Day Normandy Landings",
        "date": "1944-06-06",
        "summary": (
            "On June 6, 1944 — D-Day — Allied forces launched the largest seaborne invasion in "
            "history on the beaches of Normandy, France. Over 156,000 American, British, and "
            "Canadian troops stormed five beaches under heavy German fire. The operation, codenamed "
            "Operation Overlord, opened a crucial Western Front against Nazi Germany and is widely "
            "regarded as the turning point that led to the liberation of Western Europe."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Normandy_landings"],
    },
    {
        "title": "Atomic Bombing of Hiroshima",
        "date": "1945-08-06",
        "summary": (
            "On August 6, 1945, the United States dropped the first atomic bomb ever used in "
            "warfare on the Japanese city of Hiroshima. The explosion instantly killed an estimated "
            "80,000 people, with tens of thousands more dying from radiation exposure in the "
            "following months. The bombing — followed by a second on Nagasaki — led to Japan's "
            "surrender and the end of World War II, ushering in the nuclear age."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Atomic_bombings_of_Hiroshima_and_Nagasaki"],
    },
    {
        "title": "Indian Independence from Britain",
        "date": "1947-08-15",
        "summary": (
            "At midnight on August 15, 1947, India gained independence from nearly 200 years "
            "of British colonial rule following a mass non-violent resistance movement led by "
            "Mahatma Gandhi and the Indian National Congress. The independence was accompanied "
            "by the partition of British India into two nations — India and Pakistan — triggering "
            "one of the largest mass migrations in human history and widespread communal violence."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Indian_independence_movement"],
    },
    {
        "title": "Rosa Parks Refuses to Move",
        "date": "1955-12-01",
        "summary": (
            "On December 1, 1955, Rosa Parks, a Black seamstress in Montgomery, Alabama, refused "
            "to give up her seat on a city bus to a white passenger, defying segregation laws. "
            "Her arrest sparked the Montgomery Bus Boycott, a 381-day protest that became a "
            "landmark event in the American Civil Rights Movement and catapulted a young Dr. "
            "Martin Luther King Jr. to national prominence."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Rosa_Parks"],
    },
    {
        "title": "Gagarin Becomes First Human in Space",
        "date": "1961-04-12",
        "summary": (
            "On April 12, 1961, Soviet cosmonaut Yuri Gagarin became the first human to travel "
            "into outer space, completing one orbit of Earth aboard Vostok 1 in 108 minutes. "
            "His mission marked a historic milestone in the Space Race and demonstrated that "
            "human spaceflight was possible. Gagarin became an international hero and his flight "
            "accelerated the American commitment to reach the Moon."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Vostok_1"],
    },
    {
        "title": "Cuban Missile Crisis Begins",
        "date": "1962-10-22",
        "summary": (
            "On October 22, 1962, President John F. Kennedy informed the American public that "
            "the Soviet Union had placed nuclear missiles in Cuba, demanding their removal and "
            "imposing a naval blockade. The 13-day standoff brought the United States and Soviet "
            "Union to the closest the world has ever come to nuclear war. The crisis ended when "
            "the Soviets agreed to remove the missiles in exchange for U.S. pledges not to "
            "invade Cuba."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Cuban_Missile_Crisis"],
    },
    {
        "title": "Fall of the Berlin Wall",
        "date": "1989-11-09",
        "summary": (
            "On November 9, 1989, East Germany announced that its citizens could freely cross "
            "the Berlin Wall, the symbol of Cold War division that had split Germany since 1961. "
            "Jubilant crowds flooded the checkpoints and began tearing down the wall with hammers. "
            "The event marked the effective end of the Cold War and led directly to the "
            "reunification of Germany in 1990 and the eventual dissolution of the Soviet Union."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Berlin_Wall"],
    },
    {
        "title": "Mandela Released from Prison",
        "date": "1990-02-11",
        "summary": (
            "On February 11, 1990, Nelson Mandela walked free from Victor Verster Prison in "
            "South Africa after 27 years of imprisonment for his anti-apartheid activism. "
            "His release, ordered by President F.W. de Klerk, marked the beginning of the "
            "end of apartheid. Four years later, Mandela won South Africa's first fully "
            "democratic election and became the nation's first Black president."
        ),
        "sources": ["https://en.wikipedia.org/wiki/Nelson_Mandela"],
    },
    {
        "title": "South Africa's First Free Election",
        "date": "1994-04-27",
        "summary": (
            "On April 27, 1994, South Africans of all races voted together for the first time "
            "in the country's history, ending decades of apartheid rule. Nelson Mandela and the "
            "African National Congress won with 62% of the vote. The peaceful transition from "
            "white-minority rule to democracy was hailed as a miracle by the world and became "
            "a symbol of reconciliation and hope for oppressed peoples everywhere."
        ),
        "sources": ["https://en.wikipedia.org/wiki/1994_South_African_general_election"],
    },
]


def slugify(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_filename(event: dict) -> str:
    date = event["date"]
    slug = slugify(event["title"])
    return f"{date}-{slug}.json"


def seed():
    created = 0
    skipped = 0

    for event in EVENTS:
        filename = build_filename(event)
        path = EVENTS_DIR / filename

        if path.exists():
            print(f"  SKIP  {filename} (already exists)")
            skipped += 1
            continue

        path.write_text(json.dumps(event, indent=2), encoding="utf-8")
        print(f"  CREATE {filename}")
        created += 1

    print(f"\nDone. Created: {created}  Skipped: {skipped}  Total events: {len(EVENTS)}")


if __name__ == "__main__":
    seed()
