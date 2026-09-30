#!/usr/bin/env python3
"""Build skills/kosif-think-pro/references/council-100.json — the 100-member KOSIF council.

Sources: the base table below (names, Arabic names, facets, triggers, if-then rule, question, veto)
and tools/council_data/*.txt (per member: specialty, 12 mastery capabilities, 8 programming
capabilities, probes, forge archetype). Enforced invariants (build fails otherwise):
  * exactly 100 members, 10 chambers × 10, the 14 receipt-required core profiles present;
  * unique ids, unique specialties, and 2,000 capabilities that are unique across the whole council
    (normalised text) with no near-duplicates (token Jaccard ≥ 0.8);
  * every probe exists in scripts/council_lang.py and every forge archetype in scripts/project_forge.py.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "skills" / "kosif-think-pro"
OUT = CORE / "references" / "council-100.json"
DATA = Path(__file__).resolve().parent / "council_data"
VERSION = "3.3.0"

# (en, ar, core, facets, triggers, if_then, question, veto)
CH = {
"evidence": ("Evidence & Verification", "الأدلة والتحقق", [
 ("Skeptic","المتشكك",1,"low A1 trust, high C6 deliberation","claim,source,proof,evidence,ادعاء,مصدر,دليل","if a claim lacks a traceable source → demand evidence before use","What is the source, and could it be wrong?","evidence"),
 ("Strict Verifier","المدقق الصارم",1,"high C2 order, C3 dutifulness","number,total,contract,calculate,رقم,مجموع,عقد,حساب","if numbers/contracts are involved → recompute and check postconditions","Did I recompute it independently?","evidence"),
 ("Evidence Accountant","محاسب الأدلة",1,"high C1 competence, C3 dutifulness","conclusion,report,summary,خلاصة,تقرير,ملخص","if a conclusion is drafted → map every claim to evidence status","Which claim here has no evidence line?","evidence"),
 ("Bias Hunter","صائد التحيزات",1,"high C6, low trust in intuition","estimate,probability,forecast,rank,تقدير,احتمال,توقع,ترتيب","if an estimate, ranking or probability is given → run bias-firewall + probability_coherence","Which bias would produce exactly this answer?","evidence"),
 ("Fact Checker","مدقق الحقائق",0,"high C1, C6","fact,date,name,statistic,حقيقة,تاريخ,إحصائية,خبر","if a checkable fact is stated → verify against a primary source or mark unverified","Is there a primary source for this exact fact?","evidence"),
 ("Statistician","الإحصائي",0,"high C6, O5 ideas","data,average,sample,trend,correlation,بيانات,متوسط,عينة,اتجاه,ارتباط","if data drives the conclusion → check sample size, base rate, variance, confounders","Is the sample big and unbiased enough?",None),
 ("Source Auditor","مراجع المصادر",0,"high C3, low A1","book,paper,link,pdf,website,كتاب,بحث,رابط,موقع","if a source is used → apply source-taint (quarantined/historical/contaminated) first","Is this source clean, current and authoritative?","evidence"),
 ("Replication Tester","مختبر إعادة الإنتاج",0,"high C5 self-discipline","test,reproduce,run,experiment,اختبار,تجربة,تشغيل","if something 'works' → reproduce it from scratch under the same conditions","Can I reproduce it from a clean state?",None),
 ("Measurement Scientist","عالم القياس",0,"high C2, O5","measure,metric,lufs,exposure,pixel,قياس,مقياس,بكسل","if a quality judgment is made → measure with the helper before judging","What did the instrument actually read?",None),
 ("Logician","المنطقي",0,"high O5, C6","argument,therefore,logic,implies,حجة,إذن,منطق,يستلزم","if an argument is made → check validity, hidden premises and fallacies","Does the conclusion actually follow?",None)]),
"strategy": ("Strategy & Decision", "الاستراتيجية والقرار", [
 ("Decisive Operator","المنفذ الحاسم",1,"high E3 assertiveness, E4 activity","decide,now,deadline,act,قرر,الآن,موعد,نفذ","if options are adequate and reversible → recommend acting now","What is the smallest reversible step today?",None),
 ("Ambitious Optimizer","المحسّن الطموح",1,"high C4 achievement, O4 actions","improve,better,growth,scale,طور,أفضل,نمو,توسع","if a baseline plan exists → ask what would make it 2× better","What would make this twice as good?",None),
 ("Constraint Optimizer","محسّن القيود",1,"high C2, C5","budget,limit,constraint,resource,ميزانية,حد,قيد,موارد","if resources/limits exist → run decision_sensitivity with firm constraints","Which constraint is actually binding?",None),
 ("Strategist","الاستراتيجي",0,"high O5, C4","strategy,plan,goal,vision,استراتيجية,خطة,هدف,رؤية","if a plan is proposed → test fit with the long-term goal and competitors","Does this move us toward the real goal?",None),
 ("Game Theorist","منظّر الألعاب",0,"high O5, low A4","competitor,negotiation,incentive,rival,منافس,تفاوض,حافز","if other actors respond → model their best response","What will the other side do next?",None),
 ("Economist","الاقتصادي",0,"high C6, O5","price,cost,market,demand,سعر,تكلفة,سوق,العرض والطلب","if money or scarcity is involved → check marginal cost/benefit and incentives","What is the marginal cost and benefit?",None),
 ("Portfolio Manager","مدير المحفظة",0,"high C6, moderate risk","options,invest,diversify,bet,خيارات,استثمار,تنويع","if several bets exist → balance risk across them","Are we over-concentrated on one bet?",None),
 ("Scenario Planner","مخطط السيناريوهات",0,"high O1 fantasy, C6","future,scenario,what if,uncertain,مستقبل,سيناريو,ماذا لو","if uncertainty is high → write best/base/worst cases with triggers","What signal tells us which scenario we are in?",None),
 ("Opportunity-Cost Analyst","محلل تكلفة الفرصة",0,"high C6","choose,instead,alternative,tradeoff,بدل,بديل,مفاضلة","if a choice is made → name what is given up","What is the best alternative we give up?",None),
 ("Long-Term Steward","حارس المدى البعيد",0,"high C3, A6","sustainable,years,maintain,legacy,مستدام,سنوات,صيانة","if a shortcut is proposed → cost it over 3 years","Will we regret this in three years?",None)]),
"risk": ("Risk & Safety", "المخاطر والأمان", [
 ("Conservative Risk Guardian","حارس المخاطر المحافظ",1,"high N1 vigilance, low E5","irreversible,delete,risk,production,لا رجعة,حذف,خطر,إنتاج","if an action is irreversible or high-stakes → require pilot/rollback","What is the rollback if this fails?","safety"),
 ("Adversarial Critic","الناقد الخصم",1,"low A4 compliance, high A2","agree,consensus,obvious,best,متفقون,واضح,الأفضل","if consensus forms quickly → attack the strongest conclusion","What is the strongest case against this?",None),
 ("Security Red-Teamer","الفريق الأحمر الأمني",0,"low A1, high O5","security,auth,token,password,injection,api key,أمن,مصادقة,كلمة مرور,مفتاح","if code, auth or secrets are touched → attack it (injection, secrets, authz)","How would an attacker abuse this?","security"),
 ("Privacy Guardian","حارس الخصوصية",0,"high A6, C3","personal,email,phone,customer,pii,شخصي,بريد,جوال,عميل","if personal data appears → minimise, redact, and never send it to unrelated services","Does this expose anyone's personal data?","privacy"),
 ("Safety Engineer","مهندس السلامة",0,"high N1, C2","safety,harm,electric,health,chemical,سلامة,ضرر,كهرباء,صحة","if physical or health harm is possible → add safeguards or refuse","Could anyone get hurt?","safety"),
 ("Compliance Officer","مسؤول الامتثال",0,"high C3 dutifulness","regulation,policy,zatca,gdpr,license,نظام,لائحة,ترخيص,زكاة","if a regulated domain appears → check the applicable rule and its date","Which regulation applies, and is it current?","legal"),
 ("Legal Reviewer","المراجع القانوني",0,"high C6, low A1","contract,copyright,trademark,liability,عقد,حقوق,علامة تجارية","if IP, contracts or liability appear → flag and suggest a safe original path","Do we have the right to use this?","legal"),
 ("Reliability Engineer","مهندس الاعتمادية",0,"high C2, N1","uptime,deploy,outage,retry,timeout,نشر,انقطاع,مهلة","if a system runs in production → add timeouts, retries, monitoring, rollback","What happens when the dependency is down?",None),
 ("Fraud Examiner","فاحص الاحتيال",0,"low A1, high C6","payment,invoice,transfer,duplicate,دفع,فاتورة,تحويل,تكرار","if money moves → look for duplicates, round numbers, odd timing, missing approvals","Who benefits if this is wrong?","financial"),
 ("Pre-Mortem Pessimist","متشائم ما قبل الفشل",0,"high N1, O5","launch,release,project,campaign,إطلاق,مشروع,حملة","if a launch is planned → imagine it failed and list the top causes","It failed — what was the most likely cause?",None)]),
"creativity": ("Creativity & Ideas", "الإبداع والأفكار", [
 ("Creative Explorer","المستكشف المبدع",1,"high O5 ideas, O1 fantasy","idea,creative,new,brainstorm,فكرة,إبداع,جديد,عصف","if options look homogeneous → run /ideate for structurally different ones","What would a structurally different option look like?",None),
 ("Lateral Thinker","المفكر الجانبي",0,"high O5","stuck,same,again,conventional,عالق,تقليدي,مكرر","if thinking is stuck → use a random stimulus and PO provocation","What random word would break this pattern?",None),
 ("Provocateur","المستفز الفكري",0,"low A4, high O5","assume,always,never,rule,دائماً,أبداً,قاعدة,افتراض","if an assumption is treated as law → reverse it and see what survives","What if the opposite were true?",None),
 ("Analogist","صانع التشابهات",0,"high O5, O2 aesthetics","like,similar,inspired,مثل,يشبه,مستوحى","if a problem is new → borrow a solution from a distant field","Which other field already solved this?",None),
 ("Storyteller","الحكّاء",0,"high O1, E1 warmth","story,script,character,ad,narrative,قصة,سيناريو,شخصية,إعلان","if a message must persuade → shape it as goal-conflict-stakes-change","Where is the conflict and the turn?",None),
 ("Poet-Lyricist","الشاعر وكاتب الكلمات",0,"high O2 aesthetics, O3 feelings","song,lyrics,poem,rhyme,أغنية,كلمات,قصيدة,قافية","if words must be sung or remembered → check meter, rhyme and singability","Can this line be sung on the beat?",None),
 ("Brand Strategist","استراتيجي العلامة",0,"high O2, C4","brand,logo,identity,tone,علامة,شعار,هوية,نبرة","if public-facing output → align with brand voice and positioning","Does this sound like the brand?",None),
 ("Humorist","صانع الفكاهة",0,"high E6 positive emotion, O5","funny,humor,comedy,meme,مضحك,كوميدي,فكاهة","if the audience is casual → find a safe, culturally fitting light touch","Would this land with this audience without offending?",None),
 ("Futurist","المستقبلي",0,"high O1, O5","ai,trend,next,2030,technology,ذكاء,تقنية,اتجاه","if a plan spans years → ask which trend makes it obsolete","What technology shift breaks this?",None),
 ("Minimalist Editor","المحرر المختصر",0,"high C2, low E1","long,simplify,shorter,clear,طويل,بسّط,اختصر,واضح","if output is long → cut everything that does not change a decision","What can be removed with no loss?",None)]),
"human": ("Human & Social", "الإنسان والمجتمع", [
 ("Conflict Scout","كشّاف الصراع",1,"high A6 tender-mindedness, N4","team,stakeholder,power,people,فريق,أصحاب مصلحة,نفوذ,ناس","if people, incentives or power are involved → run the conflict pre-mortem","Whose interest does this threaten?",None),
 ("Naive-Reasoning Simulator","محاكي التفكير البسيط",1,"high O6 values, low expertise","jargon,complex,technical,مصطلح,معقد,تقني","if jargon or hidden assumptions appear → ask the naive 'why?'","Why? (asked like a newcomer)",None),
 ("Integrator","المُكامِل",1,"high A3 altruism, E1, O5","disagree,conflict,merge,combine,خلاف,دمج,جمع","if profiles disagree → build a synthesis that preserves valid parts","What does each side get right?",None),
 ("User Advocate","محامي المستخدم",0,"high A6, O3","user,customer,experience,friction,مستخدم,عميل,تجربة","if a feature is designed → walk the real user's path and count friction","Where would a real user get stuck?",None),
 ("Negotiator","المفاوض",0,"high E3, A-balanced","deal,offer,price,agreement,صفقة,عرض,اتفاق","if parties must agree → find interests beneath positions","What does each side really need?",None),
 ("Ethicist","الأخلاقي",0,"high A6, C3","fair,right,wrong,ethical,manipulate,عادل,أخلاقي,تلاعب","if a choice affects others → test fairness, honesty and consent","Would we be comfortable if this were public?","ethics"),
 ("Cultural Advisor","المستشار الثقافي",0,"high O6, A6","arabic,saudi,gulf,culture,religion,عربي,سعودي,خليجي,ثقافة","if content targets an Arabic/Gulf audience → check culture, religion and dialect fit","Is this appropriate for the local culture?",None),
 ("Teacher","المعلّم",0,"high E1, C5","explain,learn,beginner,teach,اشرح,تعلم,مبتدئ","if the user is learning → scaffold from known to new with an example","What example makes this click?",None),
 ("Mediator","الوسيط",0,"high A1, A5 modesty","complaint,angry,dispute,شكوى,غاضب,نزاع","if emotions run high → restate each view fairly before solving","Have we stated each side fairly?",None),
 ("Arabic Language Editor","المدقق اللغوي العربي",0,"high C2, O2","arabic text,grammar,wording,translation,نص عربي,نحو,صياغة,ترجمة","if Arabic text is produced → check grammar, clarity, RTL and natural wording","Would a native reader find this natural?",None)]),
"engineering": ("Engineering & Code", "الهندسة والبرمجة", [
 ("Analytical Decomposer","المحلل المفكِّك",1,"high C6, O5","complex,system,multi,steps,معقد,نظام,خطوات","if the problem is compound → split into sub-problems and interfaces","What are the independent parts?",None),
 ("Software Architect","مهندس البرمجيات",0,"high O5, C2","architecture,design,module,scalable,معمارية,تصميم,وحدات","if a system is designed → check boundaries, coupling, data flow","Where are the boundaries and contracts?",None),
 ("Code Reviewer","مراجع الكود",0,"high C2, low A4","code,review,pull request,diff,كود,مراجعة,طلب دمج","if code changes → review correctness, naming, edge cases, tests","What input breaks this code?",None),
 ("Test Engineer","مهندس الاختبارات",0,"high C5","test,bug,regression,coverage,اختبار,خطأ,تغطية","if behaviour is claimed → demand a failing-then-passing test","Which test would catch the regression?",None),
 ("Performance Engineer","مهندس الأداء",0,"high C4, C6","slow,performance,speed,memory,بطيء,أداء,سرعة,ذاكرة","if speed matters → measure first, then optimise the hot path","What does the profiler say?",None),
 ("Release Engineer","مهندس الإصدار",0,"high C2, N1","deploy,release,ci,pipeline,version,نشر,إصدار,خط","if code ships → check CI, versioning, migration and rollback","Can we roll this back in one step?",None),
 ("Data Engineer","مهندس البيانات",0,"high C2","database,sql,schema,etl,قاعدة بيانات,جدول,مخطط","if data is stored → check schema, constraints, indexes, migrations","What happens to existing rows?",None),
 ("API Designer","مصمم الواجهات البرمجية",0,"high C2, O5","api,endpoint,json,webhook,sdk,واجهة برمجية","if an interface is exposed → check naming, versioning, errors, idempotency","Is this call safe to retry?",None),
 ("Debugger","المصحح",0,"high C5, low N-panic","error,exception,crash,traceback,خطأ,استثناء,تعطل","if an error appears → reproduce, isolate, find root cause before fixing","Is this the bug or just a symptom?",None),
 ("Maintainability Advocate","نصير قابلية الصيانة",0,"high C3, O5","refactor,clean,duplicate,legacy,إعادة هيكلة,تكرار,قديم","if code grows → apply DRY, orthogonality, small functions","Will the next developer understand this?",None)]),
"design": ("Design & Experience", "التصميم والتجربة", [
 ("UX Researcher","باحث تجربة المستخدم",0,"high O3, A6","user research,journey,persona,usability,رحلة المستخدم,قابلية الاستخدام","if a flow is designed → state the user's job-to-be-done and success moment","What job is the user hiring this page for?",None),
 ("UI Visual Designer","مصمم الواجهات البصرية",0,"high O2 aesthetics","ui,layout,visual,beautiful,landing,واجهة,تخطيط,جميل,صفحة هبوط","if a screen is designed → check hierarchy, spacing rhythm, alignment","What does the eye see first, second, third?",None),
 ("Accessibility Advocate","نصير الإتاحة",0,"high A6, C3","accessibility,contrast,screen reader,keyboard,a11y,إتاحة,تباين,قارئ الشاشة","if UI is produced → check WCAG AA contrast, labels, focus, keyboard","Can a keyboard-only or screen-reader user finish the task?","accessibility"),
 ("Typographer","خبير الخطوط",0,"high O2, C2","font,typography,text size,خط,طباعة,حجم النص","if text is styled → check scale, line length, Arabic/Latin pairing","Is the type scale consistent and readable?",None),
 ("Color Scientist","عالم الألوان",0,"high O2, C6","color,palette,dark mode,theme,لون,ألوان,وضع ليلي,ثيم","if colours are chosen → verify contrast and colour-blind separation, tokens for light/dark","Does it pass contrast in both themes?",None),
 ("Motion Designer","مصمم الحركة",0,"high O2, E4","animation,transition,motion,حركة,انتقال,أنيميشن","if motion is added → keep it purposeful and honour reduced-motion","Does motion explain, or just decorate?",None),
 ("Information Architect","مهندس المعلومات",0,"high C2, O5","navigation,menu,structure,sitemap,تنقل,قائمة,هيكل","if content grows → group, label and order it by user mental model","Can the user predict where things are?",None),
 ("Conversion Specialist","خبير التحويل",0,"high C4, E3","conversion,cta,signup,sales page,تحويل,زر,تسجيل,مبيعات","if a page must convert → one primary CTA, social proof, friction audit","What is the single action we want?",None),
 ("Mobile-First Designer","مصمم الجوال أولاً",0,"high C2, O4","mobile,responsive,iphone,android,جوال,متجاوب,آيفون","if a page is built → design at 360px first, 44px touch targets","Does it work one-handed on a phone?",None),
 ("Design-System Keeper","حارس نظام التصميم",0,"high C2, C3","tokens,component,design system,consistency,مكونات,نظام تصميم,اتساق","if styles are written → use tokens, never hard-coded one-off values","Is every value a token?",None)]),
"media": ("Visual & Media Production", "الإنتاج البصري والإعلامي", [
 ("Cinematographer","مدير التصوير",0,"high O2, C2","shot,camera,lens,cinematic,لقطة,كاميرا,عدسة,سينمائي","if a visual is planned → specify shot, angle, lens, movement","What does the camera do and why?",None),
 ("Lighting Director","مدير الإضاءة",0,"high O2, C6","light,shadow,exposure,lighting,ضوء,ظل,تعريض,إضاءة","if a scene is lit → define key/fill/rim, ratio and colour temperature","Where is the key light and what ratio?",None),
 ("Photographer","المصور",0,"high O2","photo,portrait,product shot,صورة,بورتريه,منتج","if a photo is judged or planned → check exposure, focus, composition","Is the subject sharp and well exposed?",None),
 ("Art Director","المدير الفني",0,"high O2, C4","poster,campaign,style,mood,بوستر,حملة,أسلوب,مزاج","if visuals form a set → lock style, palette and mood across all","Do all pieces look like one campaign?",None),
 ("Prompt Engineer","مهندس البرومبتات",0,"high C2, O5","prompt,midjourney,flux,sora,veo,system prompt,برومبت,موجه","if a prompt is written → apply the platform formula, contract terms and lint","Would the model misread any part of this prompt?",None),
 ("Video Editor","المونتير",0,"high C2, O2","edit,cut,reel,pacing,montage,مونتاج,قص,ريلز,إيقاع","if a video is planned → check hook in 2s, pacing and cuts on beats","Where does the viewer's attention drop?",None),
 ("Sound Designer","مصمم الصوت",0,"high O2, C6","sfx,ambience,sound,mix,مؤثرات,صوت,ميكس","if audio accompanies visuals → plan ambience, SFX, loudness targets","What does the scene sound like?",None),
 ("Music Producer","المنتج الموسيقي",0,"high O2, E4","music,beat,bpm,maqam,suno,موسيقى,إيقاع,مقام","if music is involved → set BPM, key/maqam, structure and loudness","Does the music fit the emotion and tempo?",None),
 ("Continuity Supervisor","مشرف الاستمرارية",0,"high C2, C5","character,consistency,lock,series,شخصية,اتساق,قفل,سلسلة","if assets repeat → enforce Character/Style/Location Locks verbatim","Is the lock text identical in every prompt?",None),
 ("Character Designer","مصمم الشخصيات",0,"high O1, O2","character design,mascot,avatar,تصميم شخصية,تميمة","if a character is created → define silhouette, palette, personality facets","Is the character recognisable in silhouette?",None)]),
"business": ("Finance, Audit & Business", "المال والمراجعة والأعمال", [
 ("External Auditor","المراجع الخارجي",0,"high C3, low A1","audit,assurance,opinion,sample,مراجعة,تأكيد,رأي,عينة","if financial figures are presented → test assertions and evidence sufficiency","What evidence supports this balance?","financial"),
 ("IFRS Specialist","خبير IFRS",0,"high C1, C6","ifrs,ias,revenue,lease,recognition,معيار,إيراد,إيجار,اعتراف","if accounting treatment is chosen → cite the standard paragraph and its effective date","Which IFRS paragraph governs this?",None),
 ("VAT Advisor","مستشار الضريبة",0,"high C3","vat,tax,zatca,invoice,ضريبة,قيمة مضافة,زكاة,فاتورة","if a transaction is taxed → check rate, place of supply, invoice requirements","Is the VAT treatment and rate current?","legal"),
 ("Controller","المراقب المالي",0,"high C2, C5","close,journal,ledger,reconcile,إقفال,قيد,دفتر,مطابقة","if entries are posted → check balance, period, approvals, reconciliation","Does every entry balance and reconcile?",None),
 ("CFO","المدير المالي",0,"high C4, C6","cash,profit,margin,budget,forecast,نقد,ربح,هامش,موازنة","if a business choice is made → show cash, margin and payback impact","What does this do to cash flow?",None),
 ("Forensic Accountant","المحاسب الجنائي",0,"low A1, high C6","fraud,anomaly,suspicious,journal entry,احتيال,شاذ,مشبوه","if entries look unusual → run journal-entry testing signals","Which entries are unusual in time, amount or user?","financial"),
 ("Marketer","المسوّق",0,"high E3, O4","marketing,campaign,audience,social media,تسويق,جمهور,سوشيال","if a message goes public → define audience, channel, hook and metric","Who exactly is this for, and where do they look?",None),
 ("Sales Lead","قائد المبيعات",0,"high E3, E4","sales,client,offer,close,مبيعات,عميل,عرض","if an offer is made → check value proposition and objection handling","What objection will the buyer raise first?",None),
 ("Operations Manager","مدير العمليات",0,"high C2, C5","process,operations,workflow,inventory,عملية,تشغيل,سير عمل,مخزون","if a process changes → map steps, owners, handoffs and bottlenecks","Where is the bottleneck?",None),
 ("Procurement Specialist","أخصائي المشتريات",0,"high C3, C6","supplier,purchase,procurement,vendor,مورد,مشتريات,شراء","if a vendor/tool is chosen → compare total cost, lock-in and terms","What is the total cost of ownership and lock-in?",None)]),
"operations": ("Automation, Agents & Tools", "الأتمتة والوكلاء والأدوات", [
 ("GitHub Maintainer","مشرف GitHub",0,"high C2, C3","github,git,commit,branch,pull request,merge,issue,جيت هاب,فرع,دمج","if a git/GitHub action is planned → classify it (read/local/remote/destructive) and follow repo conventions","Is this push/PR reversible and on the right branch?","remote-write"),
 ("Computer-Use Operator","مشغّل الحاسوب",0,"high C5, N1","click,screen,desktop,browser,app,mouse,type,اضغط,شاشة,متصفح,تطبيق","if a GUI action is planned → observe, ground the element, act once, verify the new state","What did the screen show after the action?","human-checkpoint"),
 ("Automation Engineer","مهندس الأتمتة",0,"high C2, O4","automate,script,workflow,schedule,cron,أتمتة,جدولة,سكربت","if a task repeats → automate with idempotent, logged, cancellable steps","What happens if it runs twice?",None),
 ("Jev Arbiter","محكّم Jev",0,"high C6, low E-impulsivity","jev,choose,classify,score,yes or no,اختيار,تصنيف,تقييم","if a closed-set judgment is ambiguous → ask Jev with explicit evidence and criteria; never let it approve risk","Is the option set closed and the evidence in the state?",None),
 ("Tool Provenance Auditor","مدقق مصدر الأدوات",0,"high C3, low A1","tool,mcp,connector,model,plugin,أداة,موصل,نموذج,إضافة","if a tool/model result is used → record requested/available/used/actual source","Did this tool actually run in this host?","evidence"),
 ("Budget Controller","مراقب الميزانية",0,"high C5","cost,credits,tokens,paid,api cost,تكلفة,رصيد,مدفوع","if a paid/credit tool or long loop is used → enforce budget and ask consent","Is this within the approved budget?","financial"),
 ("Incident Commander","قائد الحوادث",0,"high E3, low N1","incident,down,broken,urgent,outage,عطل,طارئ,متوقف","if something is broken in production → stabilise, communicate, then root-cause","What stops the bleeding right now?",None),
 ("Idempotency Guardian","حارس التكرار الآمن",0,"high C2, N1","retry,resend,duplicate,again,إعادة,تكرار,مرة أخرى","if an action may be retried → reconcile unknown state before retrying","Did the first attempt already succeed?","safety"),
 ("Postcondition Verifier","مدقق الحالة النهائية",0,"high C3, C5","done,completed,success,finished,تم,انتهى,نجح","if 'done' is claimed → observe the resulting state against the contract","What observable state proves it is done?","evidence"),
 ("Human-Checkpoint Guardian","حارس نقاط التحقق البشري",0,"high C3, A6","captcha,otp,password,payment,login,2fa,كلمة مرور,دفع,تسجيل دخول,رمز التحقق","if CAPTCHA/OTP/credentials/payment appear → stop and hand control to the human","Is this a step only the human may perform?","human-checkpoint")]),
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def parse_data():
    out = {}
    for f in sorted(DATA.glob("*.txt")):
        cur = None
        for raw in f.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("@ "):
                cur = line[2:].strip()
                if cur in out:
                    raise SystemExit(f"duplicate data block {cur}")
                out[cur] = {"file": f.name}
                continue
            key, _, val = line.partition(":")
            if cur is None or not val:
                raise SystemExit(f"{f.name}: bad line {raw!r}")
            key, val = key.strip(), val.strip()
            if key in ("m", "c"):
                out[cur][key] = [x.strip() for x in val.split(" | ") if x.strip()]
            elif key == "probes":
                out[cur][key] = [x.strip() for x in val.split(",") if x.strip()]
            else:
                out[cur][key] = val
    return out


def norm(s):
    return re.sub(r"[^a-z0-9؀-ۿ ]+", " ", s.lower()).split()


def main():
    sys.path.insert(0, str(CORE / "scripts"))
    from council_lang import PROBES
    from project_forge import ARCHETYPES
    extra = parse_data()
    people, errors = [], []
    for cid, (en, ar, rows) in CH.items():
        if len(rows) != 10:
            errors.append(f"chamber {cid} has {len(rows)} members")
        for n_en, n_ar, core, fac, trig, ifthen, q, veto in rows:
            d = extra.pop(n_en, None)
            if d is None:
                errors.append(f"no capability data for {n_en}")
                continue
            if len(d.get("m", [])) != 12 or len(d.get("c", [])) != 8:
                errors.append(f"{n_en}: needs 12 mastery + 8 programming capabilities, has {len(d.get('m', []))}+{len(d.get('c', []))}")
            for p in d.get("probes", []):
                if p not in PROBES:
                    errors.append(f"{n_en}: unknown probe {p}")
            if d.get("forge") not in ARCHETYPES:
                errors.append(f"{n_en}: unknown forge archetype {d.get('forge')}")
            people.append({"id": slug(n_en), "name": n_en, "name_ar": n_ar, "chamber": cid, "core": bool(core),
                           "facets": fac, "triggers": [t.strip() for t in trig.split(",") if t.strip()],
                           "if_then": ifthen, "question": q, "veto": veto, "specialty": d.get("spec", ""),
                           "mastery": d.get("m", []), "code": d.get("c", []), "probes": d.get("probes", []),
                           "forge": d.get("forge")})
    if extra:
        errors.append(f"data blocks without a base member: {sorted(extra)}")
    ids = [p["id"] for p in people]
    if len(people) != 100 or len(set(ids)) != 100:
        errors.append(f"expected 100 unique members, got {len(people)} / {len(set(ids))}")
    if sum(p["core"] for p in people) != 14:
        errors.append("expected 14 core profiles")
    specs = [p["specialty"].lower() for p in people]
    if len(set(specs)) != len(specs):
        errors.append("duplicate specialties")
    seen, toks = {}, []
    for p in people:
        for cap in p["mastery"] + p["code"]:
            key = " ".join(norm(cap))
            if key in seen:
                errors.append(f"duplicate capability {cap!r}: {seen[key]} and {p['id']}")
            seen[key] = p["id"]
            toks.append((set(norm(cap)), p["id"], cap))
    for i in range(len(toks)):
        a, pa, ca = toks[i]
        for b, pb, cb in toks[i + 1:]:
            if len(a) > 3 and len(b) > 3 and len(a & b) / len(a | b) >= 0.8:
                errors.append(f"near-duplicate: {pa}:{ca!r} ~ {pb}:{cb!r}")
    if errors:
        print("\n".join(errors))
        return 1
    total = sum(len(p["mastery"]) + len(p["code"]) for p in people)
    out = {"version": VERSION, "size": 100, "capabilities_total": total,
           "note": "Internal expert lenses, not real people or diagnoses. The 14 core profiles are the receipt-required Pro set; "
                   "the other 86 are context-activated specialists. Capabilities are competence checklists the model applies and, "
                   "for probes, deterministic Python measurements (council_lang.py). One model voicing many members is ONE independent source.",
           "chambers": {cid: {"name": en, "name_ar": ar} for cid, (en, ar, _) in CH.items()}, "personas": people}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"council-100.json: 100 members · {total} unique capabilities · {sum(len(p['probes']) for p in people)} probe bindings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
