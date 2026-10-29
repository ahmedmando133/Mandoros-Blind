# تقييم Mandros Blind — دراسة Metformin DPP/DPPOS

## القرار

**Mandros: 38/100 — REJECT**  
**Manual extraction: 55/100 — غير مكتمل وغير صالح كـgold standard**

النتيجة لا تعني أن كل خلية لها “نسبة دقة”. هي حكم تشخيصي موزون على الأجزاء التي أمكن التحقق منها من الورقة الأصلية، مع تطبيق automatic rejection عند وجود قيمة أو arm أو timepoint خاطئ، fabrication، أو مصدر غير قابل للتحقق.

## نفس روبريك التقييم المرسل

| Domain | Weight | Mandros | Manual Excel |
|---|---:|---:|---:|
| Numerical accuracy | 30 | 13 | 22 |
| Statistical interpretation | 20 | 5 | 11 |
| PICO and eligibility | 15 | 10 | 10 |
| Outcome completeness | 15 | 4 | 3 |
| Duplication and data integrity | 10 | 1 | 5 |
| Structure and traceability | 10 | 5 | 4 |
| **Total** | **100** | **38** | **55** |

## الأخطاء المؤكدة في ملف Mandros

1. **18 outcome records تستخدم Arm IDs غير موجودة** (`ARM_MET_850` و`ARM_MET_PLA`) بينما جدول Arms يستخدم IDs مختلفة. اكتشاف الخطأ بلا إصلاح لا يجعل الملف صالحًا.
2. **783 و790 ليستا أعداد المشاركين العشوائيين ولا analyzed N عام.** هما أعداد من حضروا زيارة السنة التاسعة ضمن footnote لـTable 1. الأعداد العشوائية الصحيحة لهذه المقارنة هي placebo 1,082 وmetformin 1,073، بإجمالي 2,155.
3. **قيمة placebo 0.43 ± 4.7% تخص السنة الأولى، وليست السنة الثانية.** السنة الثانية المنشورة هي 0.02 ± 5.5%.
4. **نتائج Overall صُنفت Caucasian.** القيمة 26.5% هي metformin overall high adherence، بينما Caucasian metformin هي 29.7%.
5. **تم إنشاء baseline records غير مدعومة:** تحويل 790/783 إلى 100% Caucasian fabrication. هذه الورقة لا تعرض جدول baseline arm-level؛ الصحيح هو تسجيل `not_reported_in_this_article` بدل اختراع قيمة.
6. **Safety Outcomes شبه فارغة** رغم أن الورقة تبلغ عن GI symptoms، medication-related GI symptoms، hypoglycemia، anemia، serious anemia، hemoglobin وhematocrit.
7. **Eligibility ناقصة:** غاب استثناء BMI ≥22 kg/m² للـAsian Americans، كما غابت exclusion criteria.
8. **الجرعة والتوقيت غير مكتملين:** metformin بدأ 850 mg مرة يوميًا، ثم ارتفع بعد شهر إلى 850 mg مرتين يوميًا حسب التحمل. مجرد “850 mg twice daily” يفقد titration.
9. **فترات الدراسة خُلِطت:** التحليل double-blind في أول سنتين، DPP متوسطه 3.2 سنوات، DPPOS open-label لمدة 7–8 سنوات إضافية، والنتائج المجمعة حدها الأدنى 9 سنوات مع median follow-up نحو 10 سنوات.
10. **الـp-values غير ذرية** في عدة صفوف (`<0.001` في خلية واحدة) بدل `p_operator` و`p_value` منفصلين.
11. **التتبّع غير موثوق بالكامل:** بعض source strings paraphrased أو في صفحة غير صحيحة، وبعض سجلات Table 1 نُسبت للصفحة 2 رغم وجودها في الصفحة 3.
12. **تقارير الجودة متناقضة:** صفحة QA تعلن اكتمالًا وتحقيق gates بينما Quality Assessment يعطي REJECT و18 critical errors.

## ما الذي صححته النسخة الجديدة؟

- Arm IDs موحدة (`ARM_MET`, `ARM_PBO`) ولا توجد outcome references مكسورة.
- فصل randomized N عن year-9 visit counts.
- فصل dose، unit، initial frequency، target frequency، وtitration.
- inclusion وexclusion في سجلات منفصلة، مع subgroup-specific BMI threshold.
- baseline غير المبلغ عنه لم يُختلق.
- 18 efficacy observations، و119 adherence records، و18 safety observations، كل واحدة في صف مستقل. سجلات adherence تشمل الفئات الأربع، Overall، race/ethnicity، sex، نتائج >5% weight loss، والاختبارات الإحصائية المنشورة.
- قيمة placebo البالغة 27% عند 9 سنوات سُجلت كـoverall غير مقسمة حسب adherence؛ ولم تُنسب إلى Highly adherent كما ظهر في الملف اليدوي، لأن placebo توقف وأصبح تصنيف adherence غير منطبق.
- كل outcome يفصل timepoint، arm، measure، value، unit، dispersion، p operator، p value، وsource page.
- تم استبدال أي operator مركب بأعمدة Boolean مستقلة: `operator_gt` و`operator_eq` و`operator_lt`، وكذلك `p_gt/p_eq/p_lt` و`threshold_gt/threshold_eq/threshold_lt`. النطاقات تُحفظ في `range_min/range_max` أو حدود adherence الدنيا والعليا، مع inclusivity منفصلة.
- تم الإبقاء على وحدة hemoglobin كما طبعتها الورقة (`mg/dL as published`) مع تحذير مراجعة؛ لأنها تبدو غير معتادة سريريًا ويجب التحقق من protocol/erratum قبل pooling.
- ما زال الملف مصنفًا **source-checked core** وليس “100% complete”: يلزم independent full-PDF adjudication قبل النشر أو الميتا-أناليسز.

## وضع PRISMA

PRISMA 2020 يغطي تقرير المراجعة المنهجية: eligibility، مصادر البحث، selection، data collection، risk of bias، effect measures، synthesis، reporting bias، certainty، protocol والتوافر. لكنه **ليس** أداة لتقييم صحة RCT واحدة ولا بديلًا عن CONSORT/RoB 2/ICH E9. لذلك وضعه Mandros Blind في طبقة meta-analysis منفصلة بدل منحه “PRISMA PASS” لكل دراسة.

