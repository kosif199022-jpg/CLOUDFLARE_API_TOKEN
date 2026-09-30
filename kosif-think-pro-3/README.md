# KOSIF Think Pro 3 — v3.2.0

إضافة ChatGPT (وCodex) تجمع **عقل KOSIF Think Pro** (التفكير أولاً والتحقق والإيصالات) مع **استوديو خبراء بالقياس الحقيقي**: تحليل الصور، والرسم والتوليد، والإضاءة، والصوت، والبرمجة، والفيديو.

## التثبيت
1. ChatGPT ← **المكونات الإضافية** ← **إضافة** ← «انقر لتحميله».
2. ارفع `dist/kosif-think-pro-3.2.0.zip`.
3. ثبّت الإضافة، ثم فعّل في المحادثة: Code Interpreter (لتشغيل أدوات القياس) وتوليد الصور والبحث.

## المهارات والأوامر
| المهارة | ماذا تفعل | الأوامر | أداة القياس |
|---|---|---|---|
| 🧠 kosif-think-pro | تفكير أولاً، 28 وحدة، مجلس 14 شخصية، بوابة تناقض الأدلة، جدار التحيزات، أفكار جانبية، قرار بحساسية | `/help` `/pro` `/deep` `/verify` `/selftest` `/versions` `/ideate` `/decide` `/bias` `/library` | `evidence_consistency_check.py` `pro_receipt_verify.py` `artifact_normalize.py` `version_check.py` |
| 🔍 kosif-vision | تحليل الصور بالأرقام: التعريض، الاحتراق، الحرارة اللونية، اللوحة HEX، الحدة، الضجيج، اتجاه الضوء، التكوين، EXIF | `/analyze` `/compare` `/ocr` `/critique` `/reverse` `/score` | `image_analyze.py` |
| 🎨 kosif-image-studio | توليد وتعديل الصور بعقد تنفيذ + فحص البرومبت + قفل الشخصية والأسلوب | `/img` `/imgpro` `/edit` `/prompt` `/style` `/lock` `/batch` | `prompt_lint.py` |
| 💡 kosif-lighting | خطط إضاءة بمخطط وجداول، وحسابات التعريض والمسافة والجل | `/lightplan` `/light` `/relight` `/exposure` `/gel` | `light_calc.py` |
| 🎧 kosif-audio | قياس LUFS (BS.1770) والقمة الحقيقية وBPM والطيف، ماسترينغ، أغاني Suno بالمقامات، تعليق صوتي | `/audio` `/master` `/mix` `/song` `/voice` `/sfx` `/podcast` | `audio_analyze.py` |
| 💻 kosif-code-master | كود كامل يُختبر فعلاً، ماسح أمني، تدقيق مشاريع zip كاملة، معمارية، نشر | `/code` `/debug` `/review` `/audit` `/explain` `/arch` `/optimize` `/test` `/convert` `/sql` `/deploy` | `code_scan.py` |
| 🎬 kosif-video | قصص مبنية على الصراع (GMC+S)، قوائم لقطات، ستوري بورد، برومبتات Sora/Veo/Runway/Kling | `/story` `/video` `/shots` `/storyboard` `/reel` `/ad` | `story_lint.py` `prompt_lint.py` |
| 📒 kosif-audit-ifrs | قيود يومية، ضريبة القيمة المضافة، مطابقة بنكية، معايير IFRS، أمور مراجعة رئيسية، مصطلحات عربية | `/journal` `/reconcile` `/vat` `/ifrs` `/cam` `/audit-plan` `/evidence` `/terms` `/practice` | `ledger_check.py` |

## النسخة الخاصة بـ Claude
- **claude.ai:** الإعدادات ← Capabilities ← Skills ← Upload skill ← ارفع `dist-claude/kosif-think-pro.zip` (أو افتح ملف `kosif-think-pro.skill` واضغط Save skill).
- **Claude Code:** انسخ المجلد `kosif-think-pro/` إلى `~/.claude/skills/` أو `.claude/skills/` داخل المشروع (مُثبّت مسبقاً في هذا المستودع).
- مهارة واحدة تجمع كل الخبرات: `references/domains/*.md` لكل مجال، و`scripts/` لكل أدوات القياس. البناء: `python3 tools/build_claude_skill.py`.

## ما الجديد في 3.2.0 (الدفعة الثانية من الكتب)
- **دورة الفهم** (قبل/أثناء/بعد + «كيف أعرف؟») من كتاب Impact، و**لغة استنتاج معايرة** من Outcomes، و`calibration_check.py` لكشف المبالغة أو التهوين في درجة اليقين.
- **الاستدلال المضاد للواقع** (`/whatif`) بحالة دراسية من «هاري بوتر والطفل الملعون»: سلاسل النتائج، القيود، التحقق من هوية من يعرض المساعدة.
- **10 أمثلة عملية** (`/examples`) تعلّم ChatGPT وClaude طريقة استخدام الأداة.
- **حبكات بوكر السبع** في محرك القصص، ومفردات وصف الصور في التحليل البصري.
- الاختبارات: 95 (إضافة ChatGPT) و96 (مهارة Claude).

## ما الجديد في 3.1.0 (من قراءة مكتبة «كتب»)
- قراءة وتحليل كل ملفات المجلد مع سجل صادق لكل كتاب: ما قُرئ، ونسبة التغطية، والحالة، وأين طُبّق (`skills/kosif-think-pro/references/books/`).
- **مهارة جديدة kosif-audit-ifrs** + `ledger_check.py` (توازن القيد بالهللة، الضريبة، الفترة، منع التكرار، مطابقة الفاتورة بالبنك، «حركة البنك ليست إيراداً»).
- **محرك صراع للقصص** (`story_lint.py`) من The Conflict Thesaurus.
- **Personality Lock** للشخصيات (30 سمة فرعية + سلوك «إذا… إذن…») من Cambridge Handbook، ومجلس الشخصيات صار مبنياً على السمات.
- **70 مبدأ + قوائم فحص** من The Pragmatic Programmer داخل مهارة البرمجة، و`/design-review` و`/ml`.
- **`/ideate`** بعشوائية حقيقية (REST) من Lateral Thinking Course، و**`/decide`** بحساسية الأوزان من Convex Optimization، و**`/bias`** مع فاحص الاحتمالات (مغالطة الاقتران وإهمال المعدل الأساسي) من Smart Thinking.
- تصحيح تصنيف كتب ملوّثة: Judgment in Managerial Decision Making (فهرس فقط)، Designing Bots، Convex Optimization (الفصل الأول فقط سليم).
- الاختبارات: 84 حالة (كانت 65).

## ما الجديد في 3.0.0 مقارنة بـ 2.7.3
- **بوابة أدلة مُنمّطة**: حساب آمن للتعابير (`15%` = 0.15) + تحقق من المجموع والنسبة المئوية والنسبة والنطاق وترتيب التواريخ والوحدات. تُعزل الإجابات المخالفة لنتيجة متكررة من مصدرين مستقلين (حالة 92 محفوظة)، ويُصعَّد التعارض بين قيمتين متقاربتين.
- **إيصال "صالح بنيوياً" منفصل عن "جاهز للإكمال"**: حالة `revise` لم تعد تُعدّ إكمالاً.
- **توحيد مخرجات الوكلاء** (الأدلة/المخاطر/الاعتراضات/الافتراضات) مع تقرير بكل تغيير.
- **تفاوض الإصدارات** بين runtime والجسر وإضافة ChatGPT وحزمة Pro.
- **6 مهارات خبراء جديدة** مع 5 أدوات قياس حقيقية.
- **مجموعة اختبارات 65 حالة** (كانت 17) تشمل حالة 92 وبطة الرونين وقياسات الصوت والصورة.

## الحدود (بصدق)
- هذه تعليمات وأدوات مساعدة: لا تغيّر أوزان النموذج، ولا تضمن أن المنصة ستستدعي الأدوات.
- أدوات القياس تحتاج Python (Code Interpreter). بدونها يُذكر أن القياس لم يُنفَّذ.
- مقياس الصوت يتبع BS.1770 بدقة لكنه غير معتمد رسمياً، وBPM تقديري. تسميات الإضاءة والتكوين في تحليل الصور تقديرية مبنية على الأرقام.
- ماسح الكود استدلالي: كل نتيجة تحتاج تأكيداً، وغياب النتائج ليس دليل أمان.

## للمطوّر
```bash
python3 skills/kosif-think-pro/scripts/regression_self_test.py   # 95 اختباراً
python3 tools/build_claude_skill.py                             # يبني مهارة Claude ويختبرها (96)
python3 tools/build_zip.py                                       # يتحقق ثم يبني dist/*.zip
```
