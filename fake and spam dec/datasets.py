"""
Built-in labeled training data for TruthGuard.

Two datasets are assembled here so the app trains fully offline (no downloads):

  * Fake news   -> label 1 = FAKE/unreliable, 0 = REAL/credible
  * Spam        -> label 1 = SPAM,            0 = HAM (legit)

The data combines curated hand-written examples with light templated
augmentation so each classifier has enough signal to learn robust patterns.
If you want to plug in a real corpus (e.g. Kaggle's Fake-News or the
SMS Spam Collection), just load it into the same (texts, labels) shape.
"""

import random

random.seed(7)

# ---------------------------------------------------------------------------
# FAKE NEWS -----------------------------------------------------------------
# ---------------------------------------------------------------------------

FAKE_NEWS = [
    "BREAKING: Scientists CONFIRM the earth is flat, NASA has been lying for decades!",
    "SHOCKING: Drinking this one weird juice cures cancer overnight, doctors HATE it!",
    "You won't BELIEVE what this celebrity did — the government is hiding the truth!",
    "Miracle pill melts 20kg of fat in a week without diet or exercise, click to learn the secret!",
    "Aliens have secretly landed and world leaders are covering it up, insider reveals ALL.",
    "Vaccines contain microchips to track citizens, leaked documents prove it!",
    "Eating chocolate every day makes you lose weight instantly, study they don't want you to see.",
    "5G towers are spreading the virus, share before they delete this!",
    "Famous actor found ALIVE after fake death, the media won't report this.",
    "Man discovers ancient trick banks are terrified of, earn $5000 a day from home!",
    "The moon landing was staged in a Hollywood studio, new footage exposes it.",
    "Doctors are being paid to hide this natural remedy that reverses aging.",
    "Government secretly puts mind-control chemicals in tap water, whistleblower speaks out.",
    "This fruit kills 99% of viruses, big pharma doesn't want you to know.",
    "URGENT: New law will confiscate all savings next month unless you act now!",
    "Celebrity endorses this crypto that turns $100 into $1,000,000 in days!",
    "Breaking! Politician caught in secret deal to sell the country, no proof shown.",
    "Ancient civilization had smartphones, archaeologists stunned by cover-up.",
    "Drink lemon water at 3am to cure any disease, science can't explain it.",
    "The election was rigged by machines, millions of fake votes discovered overnight.",
    "Scientists say the sun will disappear next week, prepare for eternal darkness!",
    "This household item causes instant death, throw it away immediately!",
    "Secret society controls the weather with hidden machines, footage leaked.",
    "Miracle seed regrows lost teeth in 3 days, dentists are furious.",
    "They are hiding a cure for all diseases to keep you paying, share now!",
]

# templated fake headlines for augmentation
_fake_templates = [
    "SHOCKING: {x} cures every disease, doctors are hiding the truth!",
    "BREAKING: government secretly {y}, whistleblower exposes cover-up!",
    "You won't believe how {x} makes you rich overnight, click now!",
    "Miracle {x} melts fat instantly, big pharma HATES this!",
    "URGENT: {y} will happen next week, share before they delete this!",
    "Scientists SHOCKED: {x} reverses aging, the media won't report it!",
]
_fake_x = ["this juice", "one weird trick", "this ancient seed", "a common spice",
           "this berry", "this magnet", "this crystal", "this tea"]
_fake_y = ["banned all cash", "controls the weather", "hid alien contact",
           "put chips in vaccines", "faked the news", "rigged the markets"]

# ---------------------------------------------------------------------------
# REAL NEWS -----------------------------------------------------------------
# ---------------------------------------------------------------------------

REAL_NEWS = [
    "The central bank raised interest rates by 0.25 percent, citing persistent inflation.",
    "Researchers published a peer-reviewed study on the effects of sleep on memory.",
    "The city council approved a new budget for public transportation improvements.",
    "Officials reported that the wildfire is now 60 percent contained after rainfall.",
    "The technology company announced quarterly earnings that beat analyst expectations.",
    "A new bridge opened to traffic after three years of construction and testing.",
    "The health ministry recommended annual checkups for adults over forty.",
    "Scientists observed a rare comet passing near Earth this week, visible at dawn.",
    "The national team won the match after a late goal in the second half.",
    "Farmers welcomed the monsoon rains that improved conditions for the harvest.",
    "The university opened applications for its scholarship program next semester.",
    "Local authorities issued a heat advisory and urged residents to stay hydrated.",
    "The stock market closed slightly higher amid mixed economic data.",
    "The film festival announced its lineup of documentaries for this year.",
    "Engineers completed repairs on the highway ahead of the holiday travel season.",
    "A study found that regular exercise is linked to lower risk of heart disease.",
    "The government released updated guidelines for road safety in school zones.",
    "The museum unveiled a new exhibit featuring artifacts from the region's history.",
    "Weather forecasters predict light rain over the weekend across the coast.",
    "The company recalled a batch of products due to a labeling error, officials said.",
    "Parliament debated the new education bill during a session on Tuesday.",
    "The space agency successfully launched a satellite to monitor climate patterns.",
    "Doctors advise a balanced diet and regular sleep for better overall health.",
    "The airline added new routes connecting three regional cities starting next month.",
    "Volunteers planted over a thousand trees during the community cleanup drive.",
]

_real_templates = [
    "The {org} announced {event} after a review this week.",
    "Researchers published a study on {topic} in a peer-reviewed journal.",
    "Officials reported {event} following the meeting on Tuesday.",
    "The {org} released updated guidelines on {topic} for residents.",
    "Local authorities said {event} would begin next month.",
]
_orgs = ["health ministry", "city council", "central bank", "university",
         "transport department", "weather service", "election commission"]
_events = ["a new budget", "road repairs", "an interest rate decision",
           "a public consultation", "a vaccination drive", "a safety review"]
_topics = ["air quality", "traffic safety", "nutrition", "water conservation",
           "renewable energy", "public health"]


# ---------------------------------------------------------------------------
# SPAM ----------------------------------------------------------------------
# ---------------------------------------------------------------------------

SPAM = [
    "Congratulations! You've WON a $1000 Walmart gift card. Click http://bit.ly/win to claim NOW!",
    "URGENT: Your account has been suspended. Verify your password at http://secure-login.co immediately.",
    "You have been selected for a FREE iPhone 15! Reply YES to claim before it expires.",
    "Get rich quick! Earn $5000/week working from home. No experience needed. Sign up today!",
    "Hot singles in your area are waiting to meet you! Click here now.",
    "Final notice: your car warranty is about to expire. Call 1-800-555-0199 to renew.",
    "You owe unpaid taxes. Pay immediately via gift cards to avoid arrest. Call now.",
    "WINNER! Your mobile number won the lottery of 5,000,000. Send your bank details to claim.",
    "Cheap meds online! Buy Viagra, Cialis and more at 90% discount, no prescription needed.",
    "Double your Bitcoin in 24 hours! Send BTC to this wallet and receive 2x back guaranteed.",
    "Your package could not be delivered. Update your details at http://track-parcel.info now.",
    "Claim your inheritance of $10 million from a distant relative, contact our lawyer today.",
    "Limited time offer!!! 80% OFF luxury watches, click the link before stock runs out.",
    "Dear customer, your PayPal is limited. Log in here to restore access: http://paypa1.com",
    "Free ringtones and games! Just text JOIN to 88088. Standard rates apply.",
    "You've been pre-approved for a $25,000 loan with 0% interest. Apply in 2 minutes!",
    "Act now! Investment opportunity guaranteed to triple your money risk-free.",
    "Your Netflix payment failed. Update your card at http://netflix-billing.help to continue.",
    "Make money fast! Just pay a small fee to unlock unlimited earnings today.",
    "Congratulations, you are our 1,000,000th visitor! Click to receive your prize.",
    "URGENT reply needed: confirm your OTP and CVV to secure your bank account now.",
    "Win a brand new car! Simply forward this message to 10 friends to enter.",
    "Lonely? Chat with beautiful women now, first 100 credits FREE, click here.",
    "Your electricity will be disconnected tonight. Pay pending bill via this link immediately.",
    "Exclusive crypto signal group! Join VIP and earn 500% returns this week only.",
]

_spam_templates = [
    "Congratulations! You WON a {prize}. Click {link} to claim NOW!",
    "URGENT: your {acct} is suspended, verify at {link} immediately!",
    "Get rich quick! Earn ${n}/week from home, sign up at {link}!",
    "FREE {prize} waiting for you, reply YES before it expires!",
    "Final notice: pay your {acct} bill now at {link} to avoid disconnection.",
    "Double your money in 24 hours, send to {link} guaranteed {n}x back!",
]
_prizes = ["iPhone 15", "$1000 gift card", "brand new car", "luxury watch", "5000000 lottery"]
_links = ["http://bit.ly/win", "http://secure-verify.co", "http://claim-now.info", "www.free-prize.net"]
_accts = ["bank account", "PayPal", "Netflix", "Amazon", "electricity"]

# ---------------------------------------------------------------------------
# HAM (legit messages) ------------------------------------------------------
# ---------------------------------------------------------------------------

HAM = [
    "Hey, are we still meeting for lunch tomorrow at 1pm?",
    "Can you send me the report when you get a chance? Thanks!",
    "Happy birthday! Hope you have a wonderful day.",
    "I'll be running about ten minutes late for the call, sorry.",
    "Don't forget to pick up milk and eggs on your way home.",
    "The meeting has been moved to Thursday at 3pm in room 204.",
    "Thanks for dinner last night, it was really nice catching up.",
    "Did you finish the assignment? I'm stuck on question 4.",
    "Let's plan the trip for next month, I'll check flight prices.",
    "Your appointment with Dr. Smith is confirmed for Monday at 10am.",
    "Mom said she'll call you this evening after work.",
    "Great job on the presentation today, the client loved it.",
    "Can we reschedule our catch-up to Friday? Something came up.",
    "I sent you the photos from the weekend, let me know what you think.",
    "The package arrived safely, thank you for shipping it so fast.",
    "Reminder: team standup at 9:30am tomorrow, please be on time.",
    "I've attached the notes from today's lecture for you.",
    "Are you free this weekend to help me move some furniture?",
    "The restaurant was fully booked so I made a reservation for 8pm.",
    "Congrats on the new job! We should celebrate soon.",
    "Please review the draft and share your feedback by Wednesday.",
    "I left the keys with the neighbor, they'll hand them over.",
    "Traffic is heavy on the highway, take the side road instead.",
    "Let me know if you need anything from the grocery store.",
    "The kids finished their homework, we're heading to the park now.",
]

_ham_templates = [
    "Hey, can we meet {when} to discuss the {thing}?",
    "Don't forget the {thing} {when}, thanks!",
    "The meeting moved to {when}, see you there.",
    "Thanks for the {thing}, really appreciate it.",
    "Can you send me the {thing} {when}?",
    "Reminder: {thing} is {when}, please be on time.",
]
_when = ["tomorrow", "this evening", "on Friday", "next week", "at 3pm", "Monday morning"]
_things = ["report", "notes", "assignment", "keys", "photos", "invoice", "agenda", "slides"]


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def _augment(templates, fields, n):
    out = []
    for _ in range(n):
        t = random.choice(templates)
        kwargs = {k: random.choice(v) for k, v in fields.items()}
        try:
            out.append(t.format(**kwargs))
        except KeyError:
            pass
    return out


def build_fake_news_dataset():
    fake = list(FAKE_NEWS)
    fake += _augment(_fake_templates, {"x": _fake_x, "y": _fake_y}, 120)
    real = list(REAL_NEWS)
    real += _augment(_real_templates,
                     {"org": _orgs, "event": _events, "topic": _topics}, 120)
    texts = fake + real
    labels = [1] * len(fake) + [0] * len(real)
    return texts, labels


def build_spam_dataset():
    spam = list(SPAM)
    spam += _augment(_spam_templates,
                     {"prize": _prizes, "link": _links, "acct": _accts,
                      "n": ["500", "1000", "5000", "2"]}, 120)
    ham = list(HAM)
    ham += _augment(_ham_templates, {"when": _when, "thing": _things}, 120)
    texts = spam + ham
    labels = [1] * len(spam) + [0] * len(ham)
    return texts, labels
