# Filling the App Store page

Read this **as soon as the App Store is the goal**, before building anything. Uploading the app is only half
of it: Apple will not review anything until the page people would see is complete — description, pictures,
category, price, and a questionnaire about what the app does with data.

Voice rules, timings and the command surface live in `SKILL.md`. This file adds only what is particular to the
App Store page.

## The order, and why it is that order

1. **read what the page already has** — nothing else can be decided before this
2. **create the page** if it does not exist — theirs to do, two minutes
3. **get an app to Apple** — because Apple then spends ten to thirty minutes examining it
4. **fill the page in** — which is most of the work, and fits inside that wait
5. **they answer Apple's questions about data**
6. **ask Apple whether it is satisfied**, then stop and let them decide to submit

Step 3 before step 4 is the whole point of the sequence: the build processes while the page is being written,
so the wait costs nothing. Doing it the other way round means writing the page, then sitting still. Tell the
user the order in a sentence rather than letting them discover it as it happens.

## Mechanics

Everything the page needs is written from here. The exceptions are listed below and there are no others —
sending someone to Apple's website for anything else is a mistake, not a shortcut.

| Command | What it does |
|---|---|
| `odevio app store-status <app-key>` | reads everything from Apple; changes nothing, run it freely |
| `odevio app categories` | the 37 categories |
| `odevio app set-metadata <app-key> …` | writes text, URLs, category, price, review contact |
| `odevio app attach-build <app-key> [--version X]` | chooses which app this version publishes |
| `odevio app screenshots <app-key>` | returns the link to the picture editor |
| `odevio screenshot push <app-key>` | sends the pictures to Apple |
| `odevio privacy scan` | reads what the project's libraries declare they collect |
| `odevio app check-submittable <app-key>` | Apple's own verdict — **opens the submission, which cannot be deleted** |

| Field | Most |
|---|---|
| Name, subtitle | 30 characters each |
| Description | 4000 characters |
| Keywords | 100 characters for all of them together, comma separated |
| Promotional text | 170 characters |

**What stays with the user.** Two trips to Apple's website, once per app: **creating the page**, and
**publishing the privacy answers**. A third only if the app contains anything Apple asks about in the age
rating. Beyond those they supply the pictures, the privacy policy address, and the decisions that are theirs —
category, price, what the app says about itself. Everything else is yours.

**Two timings worth knowing.** Apple examines a build for ten to thirty minutes before it can be attached, and
keeps builds for 90 days.

## How to behave here, which differs from the rest

Elsewhere this skill keeps going without asking, because the answers are derivable and being asked is a
burden. Here that instinct is wrong in one specific way: **publishing is not reversible, and a page is a
public thing with the user's name on it.**

Act as someone who has done this many times would: check everything, say what you find, and confirm the
decisions that are theirs — which app is being published, what it says about itself, what it costs. Announce
what you have verified when it reassures, rather than staying silent and hoping.

That does not mean asking permission at every turn. It means never letting them discover, afterwards, that
something was decided on their behalf: the wrong version published, a description they never read, a price
they did not choose.

Three things to check without being asked, and to mention when they are wrong:

- **the version in their project against the one Apple holds** — the most common way to publish the wrong app
- **whether anything is still missing** before saying it is ready, using Apple's own answer rather than yours
- **whether the app has a login**, because Apple refuses a submission it cannot get into, and nothing on the
  page says so

---

## 1. Start by reading, never by asking

```bash
odevio app store-status <app-key>
```

It answers, from Apple and not from memory: does the page exist, which language it is in, which version is
open, what is filled in, how many pictures there are, which builds Apple holds, and what is still missing.

Everything it reports as present, you never mention again and never ask about. The user gets one sentence
about what is left, in their words:

> Your page needs a description, some pictures and a privacy policy link. I can write the description — the
> link is the one thing only you can provide.

There is no state kept anywhere and nothing to resume: every run reads Apple afresh, so it picks up wherever
things actually are, including changes they made on Apple's website in between or from another machine. Never
ask what they did last time.

---

## 2. The page has to be created by hand

Apple does not allow an app to be created from outside its website. Asked to, it answers:

> The resource 'apps' does not allow 'CREATE'. Allowed operations are: GET_COLLECTION, GET_INSTANCE, UPDATE

Do not apologise for it at length and do not pretend it is optional. Give the six fields and wait:

> Apple only lets an app page be created on their own site. It takes two minutes and you never do it again.
>
> Go to appstoreconnect.apple.com, Apps, then the **+** button, and fill in:
>
> - Platform: iOS
> - Name: what people will see on the App Store — it has to be unused by any other app
> - Primary language
> - Bundle ID: pick `<their bundle id>` in the list
> - SKU: `<their bundle id>` again is fine, it is only for your own records
> - User access: Full Access
>
> Tell me when it is done and I will fill in the rest.

Then re-read the state. Do not ask them to confirm anything they just typed — read it.

---

## 3. Choosing which app goes on the page

Do this before writing anything, so Apple examines the build while the page is being filled in.

This is also the step where being careless does the most damage, because everything looks fine afterwards.
Sending the app and choosing it for this version are two different things, and it is entirely possible to
publish a version from three weeks ago without anything looking wrong. So do not simply attach the newest
thing you find. **Establish which app they mean to publish**, out loud, from what `store-status` already
reported.

### Nothing has been sent yet

**Ask before building. Do not announce it and start.** Everywhere else this skill keeps going without
checking, because the next step is the only step. Here it is not: they are about to put something in front of
the public, and going straight from their laptop to the App Store skips every chance to look at it first.

Someone who has done this before would ask the question, so ask it — as a choice, not as permission:

> Apple has no version of your app yet, so one has to be sent. Before I do, how would you like to go about
> it?
>
> - **Straight to the App Store** — I build it and send it, and we carry on filling in the page
> - **Try it with testers first** — same build, but it goes to TestFlight so you and a few others can use it
>   on a real phone before anyone else sees it
> - **Just check it builds** — no sending, no page, in case you only want to know it compiles

Offer this as something to click rather than to type, since the answers can be listed.

The middle option is the one worth having, and the one nobody thinks to ask for: it is the same build, so it
costs nothing extra, and it is the only moment where a mistake is still cheap. Say so plainly if they seem
unsure — a first submission that gets refused costs days.

Once they have chosen, that is a publication build; `SKILL.md` covers running one.

### Something is there already

**Always ask before publishing a build they did not just make.** Not because reusing it is wrong — it usually
is the right thing, and saves the whole build — but because only they know whether the code has moved on
since. Nothing on the machine can tell you: a build sent this morning and a project edited this afternoon look
identical from here, and the mistake surfaces as the wrong app on the App Store.

Recommend, do not merely offer. They came here to be carried, so lead with the answer:

> Apple already has a version of your app from this morning. I can publish that one and we skip the build
> entirely.
>
> The only thing I cannot tell is whether you have changed anything since. If you have, say so and I will
> build a fresh one.

A build from more than a day or two ago deserves more than a mention — lead with the doubt rather than the
saving. Same when there is more than one, or when its version disagrees with the project's: give the facts and
pick a side, not a list of identifiers.

> Apple has two versions of your app: 1.0.3 from this morning, and 1.0.1 from March. Your project is at 1.0.4,
> so neither is quite what you have now.
>
> I can send the current version, or publish 1.0.3 as it stands. Which would you prefer?

### Attaching it

```bash
odevio app attach-build <app-key>            # the most recent usable one
odevio app attach-build <app-key> --version 1.0.3
```

It answers Apple's encryption question on the way if that was left open, which otherwise blocks the submission
with nothing on the page to explain why.

**A version that already carries a build can be pointed at a different one from here.** Apple allows it for as
long as the version is editable, so a page showing yesterday's build is a command, not a trip to Apple's site.
Only an identical build is left alone — which is what makes running this again free. When it swaps one for
another it says so, and you pass that on:

> Your page was pointing at this morning's version; it now points at the one we just sent.

Never tell someone to change the attached build on Apple's website. If a command appears to refuse, read what
it actually said — `was already attached` means the right build is in place, not that it cannot be changed.

### The three states that are not a usable build

**Still being examined.** Nothing can be attached until Apple finishes. Do not present this as a failure, and
do not make them ask again:

> Apple is checking the app you sent. There is nothing for you to do — I will keep an eye on it and carry on
> as soon as it is ready.

Carry on filling the page while it runs, and re-attach afterwards. Running the command again is harmless.

**Rejected while being examined.** Apple can finish examining a build and refuse it — a missing icon size, a
disallowed API, a bad signature. From the outside this looks exactly like the previous case, except it never
resolves, so name it rather than letting them wait:

> Apple examined the version you sent and turned it down, so it cannot be published. They will have emailed
> the reason to the account holder — send it to me and I will fix it, then we build again.

Rebuilding unchanged will be refused the same way. The reason has to be read first.

**Expired.** Apple keeps builds for 90 days:

> The last version you sent to Apple has expired — they only keep them for three months. I will build and send
> a fresh one.

---

## 4. Filling the page in

### The language is whatever Apple says it is

The page has one primary language, chosen when it was created. Two apps on the same account can differ. It is
in the state output, and everything written goes into that language.

Never assume English. Writing to a language the page does not use does not fail — it silently adds a second
language, which then has to be filled in completely as well, and an incomplete one blocks the submission.

### What to ask for, and what to write yourself

Ask only for what exists nowhere else, and in one message rather than one question at a time.

| Ask | Why it cannot be derived |
|---|---|
| **A privacy policy address** | it has to be a real page on the web, and only they can put one there |
| **A support address** | same, and Apple refuses the page without it |
| Who holds the copyright — a person or a company name | Apple requires it; you write `2026 <that name>` from it |
| What the app is for, in a sentence or two | you can write the description from it, but not invent the purpose |
| Free, or a price | a product decision |
| Whether the app contains anything made by someone else | Apple asks, and only they know |
| Whether signing in is needed to use it | if so Apple needs an account to test with, or it is refused |

Write yourself, and say you have: the description, the keywords, the subtitle, the promotional text. Do not
make them stare at an empty box.

**The privacy policy is the one that catches people out.** They hear "URL" and think it is a formality. Ask
for the thing, not the link:

> Do you have a web page saying what your app does with people's data? Apple checks the link works, so it has
> to be online somewhere — a page on your site, a public Notion page, or a free GitHub Pages site all work.

### Propose the category, do not present a menu

Reading thirty-seven categories to someone who has just told you what their app does is work you are handing
back. You know enough to choose; say which and why, in one line:

> I will file it under **Finance**, which is where budgeting apps go. Say if you would rather something else.

Only fall back on the list when the app genuinely straddles two — a fitness game, a photo editor for chefs —
and then show **two or three plausible ones**:

> This could sit in Health & Fitness or in Games. Health & Fitness gets taken more seriously; Games gets
> browsed more. Which suits what you are after?

The category matters more than it looks: it decides where the app is browsed and who Apple compares it to.
Worth one considered sentence rather than a shrug.

### Show the words before writing them to the page

**Never send text to Apple that the user has not read.** This is the page strangers will judge their app by,
with their name on it. Drafting it for them is the service; putting your draft on it unseen is not.

Two failures, and the second is worse than the first:

- Writing a description **without ever asking what the app does.** You can see the code, which tells you what
  it is made of and nothing about who it is for or why anyone would want it. A description invented from a
  file listing is a guess dressed up as their words.
- Writing it, and sending it, **in the same breath.** Even a good draft has their name on it. They get to read
  it first.

> Tell me in a line or two what your app does and who it is for — I will write the App Store text from that.

> Here is what I would put on your page. Say the word and I will set it, or tell me what to change.
>
> **Subtitle** — Track your spending in seconds
> **Description** — …
> **Keywords** — budget, spending, expenses, money, savings

Rewrite as often as they like. It costs nothing, and this is the part they will actually be judged on.

### Write it well, and say why it is written that way

Drafting is the service. Do it properly rather than paraphrasing what they said back at them, and pass on what
makes App Store text work — most people writing their first one have never thought about it.

**The first line is nearly all of it.** Apple shows two or three lines before a "more" link, and most people
never tap it. Lead with what the app does for someone, not with what it is:

> *Track every expense in two taps and see where your money actually goes.*
> rather than *An application for personal finance management built with Flutter.*

**Write for the person, not about the app.** "You" beats "the user"; a thing they can do beats a feature they
receive. Concrete beats complete: three things it does well read better than eleven listed.

**Keywords are searched, the description is not** — or barely. So do not stuff keywords into the prose; put
them in the keywords field, singular, comma separated, no spaces after commas to save characters. The app's
own name never needs to be there, nor the category name.

**Subtitle is not a slogan.** Thirty characters that add something the name does not. "Budget & expenses"
earns its place; "The best budget app!" does not, and Apple sometimes rejects superlatives.

Offer the tips as you go rather than as a lecture — one line alongside the draft:

> I have led with what it does for someone rather than how it is built, since Apple only shows the first two
> lines before people have to tap "more".

If their own wording is good, use it and say so. Someone who wrote a decent line about their own app should
see it survive, not be rewritten into something blander.

### The age rating needs one question first

`--age-rating` answers Apple's whole questionnaire as containing nothing objectionable. That is the truth for
most apps and false for some, and there is no way from here to answer any single question differently.

So ask once, plainly, before passing it:

> Does your app have anything Apple asks about — gambling, violence, sexual content, drugs, or a way to browse
> the open web inside it?

All no: pass `--age-rating`, and say in passing that you have. Any yes: **do not pass it.** That section
becomes theirs, under Age Rating on the app's page — the one conditional trip to Apple's site. Setting a wrong
answer and asking them to correct it later is worse than not setting it, because in between it is a false
declaration on a public page.

### Then put it on the page

**Write the description to a file first and pass the path.** A description has paragraphs, and a line break
inside a command is read as the end of that command — so a multi-line `--description "…"` is not the command
you listed, gets stopped for approval, and shows the user a wall of shell quoting instead of their own words.
Apostrophes and bullets make it worse. Save the text, then:

```bash
odevio app set-metadata <app-key> \
  --description-file <path> --keywords "…" --subtitle "…" \
  --support-url "…" --privacy-policy-url "…" --copyright "2026 Acme" \
  --category GAMES --free \
  --contact-first-name "…" --contact-last-name "…" \
  --contact-email "…" --contact-phone "+32 496 00 00 00" \
  --uses-third-party-content false --age-rating
```

`--description` still exists for a single line. Everything else is short enough to pass directly.

**The four contact options go together or not at all.** Apple refuses an empty name or phone, so passing only
the email fails the whole request. Either give all four or leave them all for a later run.

**Support URL and copyright are not optional**, whatever the page looks like without them. Apple lists both
among the things that stop a submission, so write them in the same run as the description rather than
discovering them at the final check.

**Write everything you have in one call.** Only what is passed gets written, so a second run is always safe —
but it is not free: every run is a separate approval the user has to read and click. Collecting the support
address, the copyright and the demo account into the same command as the description turns five interruptions
into one. Run it again when something genuinely changes, not to add a field you already had.

If the app needs an account to be used, pass `--demo-account-name` and `--demo-account-password`. Apple
refuses an app its reviewer cannot get into, and that refusal costs days.

Two things Apple insists on that nobody expects: **a price even when the app is free**, and **contact details
for the reviewer** with the phone number written with its country code.

### An address that does not answer is a warning, not a refusal

`set-metadata` opens every address given and says when one does not answer. **Pass that on as information and
carry on.** It is not a reason to stop, to ask again, or to withhold the value: a page can be going up this
afternoon, the address can be right and the site not yet deployed, and none of that is yours to arbitrate.

> Saved. One thing for later: your privacy page does not answer yet. Apple opens it during the review, so it
> needs to be live before you submit — no rush, we are nowhere near that.

Then move on without waiting for a reply. If they say they will sort it out later, that is the end of it — do
not raise it again until the final check, where it belongs.

The single exception is an address that is not a web address at all, an email say, which Apple refuses
outright and which therefore was not saved. Say that it was not saved and what is needed instead:

> Apple wants a web page for support there rather than an email, so I have left it empty for now. A contact
> page on your site does the job, or anywhere else that has a link.

Do not frame either of these as something having gone wrong. Nothing has: they are notes for later on a page
that is still being written.

### Pictures

The pictures are the user's own. Send them to the editor rather than asking them to hand files to you:

```bash
odevio app screenshots <app-key>      # returns the link
odevio screenshot push <app-key>      # sends them to Apple afterwards
```

**The rule is one line: drop them into the largest size at the top of the list.** Apple derives every smaller
phone from it, never the reverse, and asks every app for 6.5 inches at least — so a smaller slot satisfies
nothing while looking filled in.

> Here is where your pictures go: <link>
>
> Drop them in the largest size at the top. Apple makes the versions for smaller phones from it by itself, so
> that one set is all you need. Tell me when you are done.

The only thing that varies is sharpness, and it is worth two sentences in the right order. Ask for the right
size first: pictures from a large iPhone, 1290 × 2796 or above, go through untouched. Then say that anything
works as a fallback, because the editor resizes whatever is dropped into a slot to exactly the dimensions
Apple demands, flattens any transparency and saves a PNG — which is why a screenshot from an iPhone 13 Pro,
refused by App Store Connect itself, goes through from here.

> Ideally, screenshots from a big iPhone — a Pro Max sort of size. If all you have is a smaller phone, use
> them anyway: I will resize them to what Apple wants. They will be a little less sharp, which is worth
> knowing but rarely a problem.

A phone one size down is imperceptible. Anything much smaller stretches far enough to look soft, and Apple
does refuse screenshots it judges blurry or stretched, so say that before they spend the effort — then send
whatever they give you. Never refuse their pictures over this; the decision is theirs.

One behaviour that looks like a bug otherwise: **sending replaces**. The pictures already on Apple for a size
are removed and replaced by the ones being sent. Other sizes are untouched.

---

## 5. The privacy questionnaire — the one thing that cannot be automated at all

Apple keeps this behind its own website. There is no way to read it or to fill it in from outside, so this
step is the user's, always.

Three things to tell them, because each one costs a wasted trip otherwise:

**Filling it in is not enough — it has to be published.** There is a separate Publish button, and until it is
pressed Apple behaves as though nothing was answered. Its own words: *"You must have published answers to your
app's data usages."*

**Only an Admin on their Apple team can do it.** If they are not one, no amount of guidance helps and they
need someone who is. Worth finding out before they start, not after.

**Knowing what to answer is the hard part, not the clicking.** Help with that:

```bash
odevio privacy scan
```

It reads what the project's libraries declare they collect and prints it under the exact headings Apple uses,
so the questionnaire becomes a matter of ticking what is listed. It also says plainly what no library can know
— what their own code collects — and asks about that instead of guessing.

> Apple wants to know what your app does with people's data. I have read what your app's libraries declare,
> which covers most of it. Here is what to tick, and the few things only you can answer.

Two things about the questionnaire itself that save a beginner from over-answering, since both are buried in
Apple's small print:

**Not everything collected has to be declared.** Data may be left out when *all* of the following hold: it is
not used for tracking, not used for advertising or marketing, collected only occasionally and outside the
app's main purpose, optional for the user, and visible to them as they provide it. Apple's own example is a
feedback form. If any one of those fails, it must be declared.

**"Collected" is narrower than it sounds.** If the app uses a payment service and the card details are typed
outside the app, where the developer never sees them, that is not collection and is not declared. The same
reasoning applies wherever the data never reaches them.

Someone answering for the first time will over-declare out of caution, and over-declaring is not harmless: it
appears on their public page as things their app takes. Say so.

---

## 6. Asking Apple whether it is ready, then stopping

```bash
odevio app check-submittable <app-key>
```

Use it when they believe they are finished, **not** as a progress check — `store-status` is for that. This one
opens the submission the app will be published with, and Apple does not allow a submission to be deleted.
That is a fair trade at the right moment and a mess at the wrong one, so say what you are doing:

> Let me ask Apple directly whether anything is still missing. This starts the submission we will publish
> with.

What comes back is authoritative, including which picture sizes this app must provide. If it says something is
missing, that is the truth even when our own reading said otherwise.

When it says the page is ready, **stop and tell them. Do not submit.**

> Everything Apple asked for is filled in and your app is ready to submit. Once submitted, a reviewer at Apple
> looks at it and nothing on the page can be changed until they answer — usually a day or two. Say the word
> and I will send it.

Submitting is not reversible from here and freezes everything. Someone publishing for the first time may not
know that, which is exactly why it is not a step to take on their behalf.

**When they say yes, you send it. Do not send them to Apple's website.**

```bash
odevio app submit <app-key> --confirm
```

`--confirm` is required, so this can never happen by accident. Apple is asked once more on the way, so an
incomplete page comes back with what is missing rather than being sent. Only their explicit yes justifies
running it — never a guess at what they meant, and never to see whether it works.
