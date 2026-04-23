# 📚 Rekxare Dami - ڕێکخەرێ دەمی

ئامیرەک بو رێکخستنا دەمێ خواندنێ ب زمانێ بادینی | Study time organizer in Badini Kurdish

---

## 🌍 الوصف | Description

<div dir="rtl">

### العربية

**Rekxare Dami** هو تطبيق ويب مجاني لتنظيم وقت الدراسة، موجه للطلاب الناطقين باللهجة البادينية (الكردية الشمالية). يتيح التطبيق للمستخدم اختيار المادة الدراسية، وضبط مؤقت زمني، ثم متابعة تقدمه عبر دائرة حية تمتلئ تدريجياً مع مرور الوقت.

**الميزات الرئيسية:**
- ⏱️ مؤقت حي بعدّ تنازلي مع دائرة تقدم مرئية.
- ⏸️ إيقاف مؤقت واستئناف للجلسة.
- 🔄 إعادة ضبط الوقت.
- 📊 إحصائيات الجلسة (إجمالي وقت الدراسة، عدد الجلسات المكتملة، آخر مادة).
- 📋 سجل بآخر الجلسات مع الوقت والتاريخ.
- 💾 حفظ دائم للبيانات (حتى بعد إغلاق المتصفح).
- 🌓 الوضع الليلي (Dark Mode).
- 💬 رسائل تحفيزية عشوائية بالبادينية.
- 📱 واجهة متجاوبة تعمل على الجوال والحاسوب.

</div>

### English

**Rekxare Dami** is a free web application for organizing study time, designed for Badini (Northern Kurdish) speaking students. The user selects a subject, sets a timer, and watches a live circular progress bar fill as time passes.

**Key Features:**
- ⏱️ Live countdown timer with visual progress circle.
- ⏸️ Pause and resume functionality.
- 🔄 Timer reset.
- 📊 Session statistics (total study time, completed sessions, last subject).
- 📋 Session history with time and date.
- 💾 Persistent data storage (survives browser close).
- 🌓 Dark Mode toggle.
- 💬 Random motivational quotes in Badini Kurdish.
- 📱 Responsive design for mobile and desktop.

---

## 🛠️ التقنيات المستخدمة | Tech Stack

| التقنية | الوصف |
| :--- | :--- |
| **Python** | لغة البرمجة الأساسية. |
| **Streamlit** | إطار عمل لبناء واجهة المستخدم. |
| **SVG + HTML/CSS** | لرسم الدائرة الحية وتنسيق الواجهة. |
| **JSON** | لحفظ البيانات محلياً. |
| **Streamlit Cloud** | لاستضافة التطبيق مجاناً. |

---

## 🚀 التشغيل | Getting Started

### جرب التطبيق مباشرة | Try it Live

🔗 **[Rekxare Dami على Streamlit Cloud](https://rekxare-dami.streamlit.app/)**

### تشغيل محلي | Run Locally

```bash
# استنساخ المستودع
git clone https://github.com/HayhatDev/rekxare-dami.git
cd rekxare-dami

# تثبيت المتطلبات
pip install streamlit

# تشغيل التطبيق
streamlit run planner.py
