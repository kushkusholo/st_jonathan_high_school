from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from datetime import datetime

# Create PDF
pdf_file = r"c:\Users\MAIKI PC\Desktop\education_codes\school_chatbot\Statistical_Tools_Chemistry_MAIKI_PROTUS.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for PDF elements
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=10,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#2e5c8a'),
    spaceAfter=8,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=10,
    leading=14
)

meta_style = ParagraphStyle(
    'MetaInfo',
    parent=styles['Normal'],
    fontSize=10,
    alignment=TA_CENTER,
    spaceAfter=4
)

# Title Page
elements.append(Spacer(1, 0.8*inch))
elements.append(Paragraph("Statistical Tools for the Chemistry Technologist:", title_style))
elements.append(Paragraph("From Classroom to Industry", title_style))
elements.append(Spacer(1, 0.5*inch))

elements.append(Paragraph("Student Name: MAIKI PROTUS", meta_style))
elements.append(Paragraph("Student Registration No.: 22/U/STC/1609/PD", meta_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Course Code: DSC 2201: Engineering Mathematics", meta_style))
elements.append(Paragraph("Lecturer: MR. KINABEYO MOSES", meta_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Institution: Kyambogo University", meta_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Date: April 13, 2026", meta_style))

elements.append(PageBreak())

# Section 1: Introduction
elements.append(Paragraph("1. Introduction", heading_style))
elements.append(Paragraph(
    "A chemistry technologist is a practical scientist who turns laboratory measurements into reliable decisions. In the workplace, a chemistry technologist performs experiments, records data, checks results against specifications, and reports findings to supervisors, clients, or regulators. Employers expect technologists to understand statistics because raw numbers by themselves do not prove quality, accuracy, or consistency.",
    body_style
))
elements.append(Paragraph(
    "Accuracy means getting the right number, while precision means getting the same number repeatedly. In chemistry, a result can be accurate but not precise, or precise but not accurate. Statistical tools help assess both. For example, repeated titration measurements may be precise if they are close together, but if they are all offset from the true value, they are not accurate. Without statistics, it is hard to know whether differences are real or just due to random variation.",
    body_style
))
elements.append(Paragraph(
    "Statistical tools move us from raw data to defensible decisions by showing when differences are significant and when they are likely due to chance. In this report, I discuss three key tools:",
    body_style
))

bullet_points = [
    "<b>t-distribution:</b> for comparing averages when sample sizes are small and the population standard deviation is unknown.",
    "<b>Chi-square distribution:</b> for comparing counts, distributions, and whether variability is acceptable.",
    "<b>F-distribution:</b> for comparing variances and checking whether two methods or instruments are equally precise."
]
for point in bullet_points:
    elements.append(Paragraph("• " + point, body_style))

elements.append(Paragraph(
    "These tools are not just classroom exercises; they are used in quality control, environmental testing, food and beverage production, pharmaceutical manufacturing, and many other industry settings.",
    body_style
))

elements.append(PageBreak())

# Section 2: t-Distribution
elements.append(Paragraph("2. The t-Distribution", heading_style))

elements.append(Paragraph("2.1 What is it?", subheading_style))
elements.append(Paragraph(
    "The t-distribution is a statistical distribution used to make inferences about a population mean when the sample size is small and the population standard deviation is unknown. It looks like a normal curve but has heavier tails, which means it allows more uncertainty for small samples.",
    body_style
))
elements.append(Paragraph(
    "We use the t-distribution instead of the normal distribution when the sample size is small (usually n &lt; 30), the population standard deviation is unknown, and the data are approximately normally distributed.",
    body_style
))
elements.append(Paragraph(
    "<b>Degrees of freedom (df):</b> are the number of independent values that can vary when estimating a statistic. For a sample mean, df = n - 1. For example, if you measure 4 titrations, you can freely choose 3 of the results, and the fourth is fixed once the mean is known. That gives df = 3.",
    body_style
))
elements.append(Paragraph(
    "<b>Confidence interval:</b> is a range that likely contains the true population mean. The t-distribution helps create a confidence interval when we estimate the standard deviation from the sample. For example, a 95% confidence interval means we are 95% confident that the true mean lies within that range.",
    body_style
))
elements.append(Paragraph(
    "<b>Statistical significance:</b> means the observed result is unlikely to occur by chance if the null hypothesis is true. In a t-test, if the calculated t-value is larger than the critical t-value, we say the result is statistically significant and reject the null hypothesis.",
    body_style
))

elements.append(Paragraph("2.2 Connection to Chemistry Courses", subheading_style))
elements.append(Paragraph(
    "In analytical chemistry and quantitative analysis practicals, one frequently performs titrations, measures absorbance with a spectrophotometer, weighs samples on an analytical balance, and calculates means and standard deviations. One common experiment is titrating a standard sodium hydroxide solution to determine the concentration of an acid sample. After repeating the titration several times, the average titre is calculated and compared to the known concentration.",
    body_style
))

elements.append(Paragraph("2.3 Connection to Industry", subheading_style))
elements.append(Paragraph(
    "<b>Industry chosen: Pharmaceutical Quality Control</b>",
    body_style
))
elements.append(Paragraph(
    "<b>Scenario:</b> As a pharmaceutical quality control technician, tablets from a batch must be tested where the label claims each tablet contains 500 mg of paracetamol. A t-test helps answer whether the batch mean is significantly different from 500 mg. The decision is whether to release the batch or reject it.",
    body_style
))
elements.append(Paragraph(
    "The t-test matters because a batch that is below specification may fail regulatory requirements or harm patients, while a batch that is within specification can be released safely. The company needs this decision to ensure product safety, comply with regulations, and avoid costly recalls.",
    body_style
))

elements.append(Paragraph("2.4 Worked Example: Pharmaceutical Quality Control", subheading_style))
elements.append(Paragraph(
    "<b>Task:</b> Test whether a sample from a batch deviates significantly from 500 mg.",
    body_style
))
elements.append(Paragraph(
    "<b>Data:</b> 498, 502, 497, 501, 499, 503, 496, 502",
    body_style
))

elements.append(Paragraph("<b>Step 1: Mean and Sample Standard Deviation</b>", body_style))
elements.append(Spacer(1, 0.1*inch))

# Data table for deviations
data = [
    ['Value (x)', 'Deviation (x - x̄)', 'Squared Deviation (x - x̄)²'],
    ['498', '-1.75', '3.0625'],
    ['502', '2.25', '5.0625'],
    ['497', '-2.75', '7.5625'],
    ['501', '1.25', '1.5625'],
    ['499', '-0.75', '0.5625'],
    ['503', '3.25', '10.5625'],
    ['496', '-3.75', '14.0625'],
    ['502', '2.25', '5.0625'],
    ['Total', '', '47.5000'],
]

table = Table(data, colWidths=[2*inch, 2.2*inch, 2.2*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
]))
elements.append(table)
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph(
    "Sum of values: Σx = 3998<br/>Sample size: n = 8<br/>Sample mean: x̄ = 3998/8 = 499.75 mg",
    body_style
))
elements.append(Spacer(1, 0.15*inch))
elements.append(Paragraph(
    "Sample variance: s² = 47.5/(8-1) = 47.5/7 = 6.7857 (mg)²",
    body_style
))
elements.append(Paragraph(
    "Sample standard deviation: s = √6.7857 = 2.605 mg (rounded to 3 decimal places)",
    body_style
))

elements.append(Paragraph("<b>Step 2: Hypotheses</b>", body_style))
elements.append(Paragraph(
    "H₀: The batch mean is equal to 500 mg (no significant difference)<br/>H₁: The batch mean is different from 500 mg (significant difference)",
    body_style
))

elements.append(Paragraph("<b>Step 3: Calculate t-statistic</b>", body_style))
elements.append(Paragraph(
    "The one-sample t-statistic formula is: t = (x̄ - μ) / (s / √n)<br/><br/>"
    "Where: x̄ = 499.75 mg (sample mean), μ = 500 mg (hypothesized population mean), "
    "s = 2.605 mg (sample standard deviation), n = 8 (sample size)",
    body_style
))
elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph(
    "Standard error calculation:<br/>"
    "√8 = 2.828<br/>"
    "SE = 2.605 / 2.828 = 0.921 mg",
    body_style
))
elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph(
    "t-statistic calculation:<br/>"
    "t = (499.75 - 500) / 0.921 = -0.25 / 0.921 = <b>-0.271 ≈ -0.27</b>",
    body_style
))

elements.append(Paragraph("<b>Step 4: Find Critical t-value</b>", body_style))
elements.append(Paragraph(
    "Degrees of freedom: df = n - 1 = 8 - 1 = 7<br/>"
    "Significance level: α = 0.05 (two-tailed test)<br/>"
    "Critical value (from t-distribution table): t<sub>critical</sub> ≈ ±2.365",
    body_style
))

elements.append(Paragraph("<b>Step 5: Decision</b>", body_style))
elements.append(Paragraph(
    "|t<sub>calculated</sub>| = |-0.27| = 0.27<br/>"
    "t<sub>critical</sub> = 2.365<br/>"
    "Since 0.27 &lt; 2.365, we <b>fail to reject H₀</b>",
    body_style
))

elements.append(Paragraph("<b>Step 6: Interpretation</b>", body_style))
elements.append(Paragraph(
    "<b>Report to Quality Control Manager:</b> The sample mean of 8 tablets is 499.75 mg, which is very close to the target of 500 mg. The t-test shows that the difference of 0.25 mg is not statistically significant at the 95% confidence level. The calculated t-value of -0.27 is much smaller in magnitude than the critical value of 2.365, meaning the observed difference is well within the range of normal variation expected from the standard deviation.",
    body_style
))
elements.append(Paragraph(
    "Therefore, there is no evidence that the batch mean deviates from the labelled strength of 500 mg. <b>The batch may be released.</b>",
    body_style
))

elements.append(PageBreak())

# Section 3: Chi-Square
elements.append(Paragraph("3. The Chi-Square Distribution", heading_style))

elements.append(Paragraph("3.1 What is it?", subheading_style))
elements.append(Paragraph(
    "The chi-square (χ²) distribution is a statistical distribution used for tests involving counts and variance. It is always positive and skewed to the right.",
    body_style
))
elements.append(Paragraph(
    "There are two main uses in chemistry:<br/>"
    "• <b>Goodness of fit:</b> checking whether observed counts match expected counts.<br/>"
    "• <b>Test of variance:</b> checking whether observed variability is within acceptable limits.",
    body_style
))

elements.append(Paragraph("3.2 Connection to Chemistry Courses", subheading_style))
elements.append(Paragraph(
    "In practical labs, one counts outcomes such as colonies on an agar plate, types of crystals under a microscope, the number of drops until a titration endpoint, and how many samples pass or fail a simple test.",
    body_style
))

elements.append(Paragraph("3.3 Connection to Industry", subheading_style))
elements.append(Paragraph(
    "<b>Industry chosen: Food and Beverage</b>",
    body_style
))
elements.append(Paragraph(
    "<b>Scenario:</b> In beverage development, a company runs a taste test asking consumers whether they like, feel neutral about, or dislike a new flavor. Marketing expects an equal distribution if the drink has no strong appeal. A chi-square goodness-of-fit test answers whether consumer preferences differ significantly from equal proportions.",
    body_style
))

elements.append(Paragraph("3.4 Worked Example: Taste Testing", subheading_style))
elements.append(Paragraph(
    "<b>Task:</b> Analyze consumer preference data for a new soft drink flavor.",
    body_style
))
elements.append(Spacer(1, 0.1*inch))

# Chi-square data table
chi_data = [
    ['Preference Category', 'Observed Frequency', 'Expected Frequency'],
    ['Liked', '70', '50'],
    ['Neutral', '40', '50'],
    ['Disliked', '40', '50'],
    ['Total', '150', '150'],
]

chi_table = Table(chi_data, colWidths=[2*inch, 2.2*inch, 2.2*inch])
chi_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
]))
elements.append(chi_table)
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("<b>Step 1: Hypotheses</b>", body_style))
elements.append(Paragraph(
    "H₀: Observed preferences match expected equal distribution<br/>"
    "H₁: Observed preferences differ from expected distribution",
    body_style
))

elements.append(Paragraph("<b>Step 2: Chi-Square Calculation</b>", body_style))
elements.append(Spacer(1, 0.1*inch))

# Chi-square calculation table
chi_calc = [
    ['Category', 'O', 'E', 'O - E', '(O - E)²', '(O - E)²/E'],
    ['Liked', '70', '50', '20', '400', '8.00'],
    ['Neutral', '40', '50', '-10', '100', '2.00'],
    ['Disliked', '40', '50', '-10', '100', '2.00'],
    ['Total', '150', '150', '', '600', '12.00'],
]

chi_calc_table = Table(chi_calc, colWidths=[1.2*inch, 0.7*inch, 0.7*inch, 0.9*inch, 1.1*inch, 1.1*inch])
chi_calc_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
]))
elements.append(chi_calc_table)
elements.append(Spacer(1, 0.15*inch))
elements.append(Paragraph(
    "χ² = 8.00 + 2.00 + 2.00 = <b>12.00</b>",
    body_style
))

elements.append(Paragraph("<b>Step 3: Degrees of Freedom</b>", body_style))
elements.append(Paragraph(
    "df = number of categories - 1 = 3 - 1 = <b>2</b>",
    body_style
))

elements.append(Paragraph("<b>Step 4: Critical Value</b>", body_style))
elements.append(Paragraph(
    "At α = 0.05 and df = 2, from the chi-square distribution table: χ²<sub>critical</sub> ≈ <b>5.99</b>",
    body_style
))

elements.append(Paragraph("<b>Step 5: Decision</b>", body_style))
elements.append(Paragraph(
    "χ²<sub>calculated</sub> = 12.00<br/>"
    "χ²<sub>critical</sub> = 5.99<br/>"
    "Since 12.00 &gt; 5.99, we <b>reject H₀</b>",
    body_style
))

elements.append(Paragraph("<b>Step 6: Interpretation</b>", body_style))
elements.append(Paragraph(
    "<b>Report to Marketing Manager:</b> The taste test results show a statistically significant preference distribution (χ² = 12.00, df = 2, p &lt; 0.05). More consumers liked the new flavor (70) than would be expected if preference were equally distributed (50). This suggests the flavor has a strong appeal. The company should consider this a positive signal and proceed with market launch.",
    body_style
))

elements.append(PageBreak())

# Section 4: F-Distribution
elements.append(Paragraph("4. The F-Distribution", heading_style))

elements.append(Paragraph("4.1 What is it?", subheading_style))
elements.append(Paragraph(
    "The F-distribution is used to compare two variances. It is the ratio of one sample variance to another sample variance. The F-distribution is always positive and is skewed to the right.",
    body_style
))
elements.append(Paragraph(
    "The F-distribution is used to compare the spread of two sets of data, to check equality of variances before applying some t-tests, and in ANOVA to compare multiple group means.",
    body_style
))

elements.append(Paragraph("4.2 Connection to Chemistry Courses", subheading_style))
elements.append(Paragraph(
    "In chemistry practicals, precision matters when using different pipettes or burettes, comparing results from two students performing the same titration, weighing the same sample multiple times on different balances, and repeating an experiment on different days.",
    body_style
))

elements.append(Paragraph("4.3 Connection to Industry", subheading_style))
elements.append(Paragraph(
    "<b>Industry chosen: Environmental Laboratory</b>",
    body_style
))
elements.append(Paragraph(
    "<b>Scenario:</b> In an environmental testing lab, a new spectrophotometer is introduced for nitrate testing. Before using it for client samples, the lab must verify that its precision matches the old trusted instrument. An F-test compares variances from repeated measurements on each instrument.",
    body_style
))

elements.append(Paragraph("4.4 Worked Example: Instrument Comparison", subheading_style))
elements.append(Paragraph(
    "<b>Task:</b> Compare the precision of two spectrophotometers for nitrate measurement.",
    body_style
))
elements.append(Paragraph(
    "<b>Data:</b><br/>"
    "Old instrument: variance s₁² = 0.25 (mg/L)², sample size n₁ = 10<br/>"
    "New instrument: variance s₂² = 0.64 (mg/L)², sample size n₂ = 10",
    body_style
))

elements.append(Paragraph("<b>Step 1: Hypotheses</b>", body_style))
elements.append(Paragraph(
    "H₀: σ₁² = σ₂² (The variances are equal)<br/>"
    "H₁: σ₁² ≠ σ₂² (The variances are not equal)",
    body_style
))

elements.append(Paragraph("<b>Step 2: Calculate F-statistic</b>", body_style))
elements.append(Paragraph(
    "Place the larger variance in the numerator:<br/>"
    "F = s₂² / s₁² = 0.64 / 0.25 = <b>2.56</b>",
    body_style
))

elements.append(Paragraph("<b>Step 3: Degrees of Freedom</b>", body_style))
elements.append(Paragraph(
    "Numerator (df₁) = n₂ - 1 = 10 - 1 = <b>9</b><br/>"
    "Denominator (df₂) = n₁ - 1 = 10 - 1 = <b>9</b>",
    body_style
))

elements.append(Paragraph("<b>Step 4: Critical Value</b>", body_style))
elements.append(Paragraph(
    "At α = 0.05, df₁ = 9, df₂ = 9, from the F-distribution table: F<sub>critical</sub> ≈ <b>3.18</b>",
    body_style
))

elements.append(Paragraph("<b>Step 5: Decision</b>", body_style))
elements.append(Paragraph(
    "F<sub>calculated</sub> = 2.56<br/>"
    "F<sub>critical</sub> = 3.18<br/>"
    "Since 2.56 &lt; 3.18, we <b>fail to reject H₀</b>",
    body_style
))

elements.append(Paragraph("<b>Step 6: Interpretation</b>", body_style))
elements.append(Paragraph(
    "<b>Report to Lab Manager:</b> The F-test shows that the new spectrophotometer does not have a significantly different variance from the old instrument (F = 2.56, df₁ = 9, df₂ = 9, p &gt; 0.05). Although the new instrument shows slightly higher variance (0.64 vs 0.25), this difference is not statistically significant.",
    body_style
))
elements.append(Paragraph(
    "Therefore, the new instrument can be accepted for routine nitrate testing and can be used interchangeably with the old one.",
    body_style
))

elements.append(PageBreak())

# Section 5: Comparison
elements.append(Paragraph("5. Comparison and Reflection", heading_style))

elements.append(Paragraph("5.1 Comparing the Three Tools", subheading_style))
elements.append(Spacer(1, 0.1*inch))

comparison_data = [
    ['Feature', 't-Distribution', 'Chi-Square Distribution', 'F-Distribution'],
    ['What does it compare?', 'Means (averages)', 'Counts or variance', 'Variances (spread)'],
    ['What type of data?', 'Continuous numerical', 'Categorical counts', 'Continuous variance'],
    ['When to use?', 'Comparing sample mean to target', 'Observed vs expected counts', 'Comparing two variances'],
    ['Industry example', 'Pharmaceutical QC: tablet strength', 'Food & Beverage: taste preference', 'Environmental Lab: instrument precision'],
]

comp_table = Table(comparison_data, colWidths=[1.3*inch, 1.4*inch, 1.5*inch, 1.4*inch])
comp_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 8.5),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
]))
elements.append(comp_table)
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("5.2 Reflection Questions", subheading_style))

elements.append(Paragraph(
    "<b>1. Which industry interests you most and why?</b><br/>"
    "I am most interested in the pharmaceutical industry because it combines quality control with the need to protect patient safety. The idea of testing tablet strength and ensuring product consistency fits well with my goal of working as a chemistry technologist in a regulated laboratory. Pharmaceutical QC requires precision, accountability, and understanding the statistical basis for regulatory decisions.",
    body_style
))

elements.append(Paragraph(
    "<b>2. How do the t-test and F-test relate to accuracy and precision?</b><br/>"
    "The t-test relates to accuracy because it checks whether a measured mean matches the expected target value. For example, a tablet's mean strength should match the labelled claim. The F-test relates to precision because it compares the consistency (spread) of two sets of measurements by comparing their variances. A precise instrument produces consistent results with low variance.",
    body_style
))

elements.append(Paragraph(
    "<b>3. Interview answer about the importance of the t-test:</b><br/>"
    "I would explain that the t-test is important because it helps us know whether a difference in average results is real or just due to random variation. For example, in quality control I might use a t-test to decide whether the mean strength of tablets is significantly different from the labelled amount. Without the t-test, I would have no objective way to distinguish between acceptable variation and genuine problems.",
    body_style
))

elements.append(Paragraph(
    "<b>4. Why do chemistry students need math?</b><br/>"
    "Chemistry relies on numbers to describe concentrations, purities, and quality. Statistics turn raw experimental data into evidence-based decisions, so math is essential for understanding whether results are reliable and whether a product meets specifications. Math provides the language and tools to communicate scientific findings clearly and defensibly.",
    body_style
))

elements.append(Paragraph(
    "<b>5. Which distribution will you use most often and why?</b><br/>"
    "I expect to use the t-distribution most often in my career because I will frequently compare measured averages to specifications, such as the concentration of a solution or the potency of a drug. For example, in pharmaceutical QC I would use the t-test to check batch mean assay results against the labelled claim. This is a fundamental task in quality control work.",
    body_style
))

elements.append(Paragraph(
    "<b>6. Why understand the tests even if software calculates them?</b><br/>"
    "Understanding the tests is important because software can only be trusted if you know the assumptions, correct inputs, and how to interpret the output. Knowing the meaning of the test prevents misuse and ensures that decisions are based on appropriate statistical evidence. A technologist who blindly trusts software results without understanding them will make mistakes when assumptions are violated or data is incorrect.",
    body_style
))

elements.append(PageBreak())

# References
elements.append(Paragraph("6. References", heading_style))
elements.append(Spacer(1, 0.1*inch))

references = [
    "Miller, J.N. and Miller, J.C., 2018. <i>Statistics and Chemometrics for Analytical Chemistry</i>. 7th ed. Pearson.",
    "Kyambogo University, 2026. <i>DSC 2201 Engineering Mathematics Lecture Notes</i>.",
    "Course Material: <i>CHM 201 Analytical Chemistry Lab Manual</i>, Kyambogo University.",
    "NIST, 2023. <i>Engineering Statistics Handbook</i>. [online] Available at: https://www.itl.nist.gov/div898/handbook/",
    "ISO, 2017. <i>ISO 17025: General requirements for the competence of testing and calibration laboratories</i>.",
    "Statistical tables: t-distribution, Chi-square distribution, F-distribution tables from course material.",
]

for i, ref in enumerate(references, 1):
    elements.append(Paragraph(f"{i}. {ref}", body_style))

# Build PDF
doc.build(elements)
print(f"✓ PDF created successfully: {pdf_file}")
