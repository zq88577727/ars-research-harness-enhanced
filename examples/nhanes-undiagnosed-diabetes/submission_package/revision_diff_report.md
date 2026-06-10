# Revision Diff Report

Before: `examples/nhanes-undiagnosed-diabetes/checkpoints/stage-S7b-citation-clean-draft.md`
After: `examples/nhanes-undiagnosed-diabetes/checkpoints/stage-S8b-revised-manuscript.md`

## Summary

- Added lines: 75
- Removed lines: 37
- Diff lines: 239

## Added Headings

- # S8b Revised Manuscript Draft
- # Tables and Figures
- # Data Availability
- # Ethics Statement

## Removed Headings

- # S7b Draft: Citation-Clean English SCI Manuscript Draft
- # Tables and Figures To Be Inserted

## Unified Diff

```diff
--- before
+++ after
@@ -1,4 +1,4 @@
-# S7b Draft: Citation-Clean English SCI Manuscript Draft
+# S8b Revised Manuscript Draft
 
 ## Manuscript Title
 
@@ -6,7 +6,7 @@
 
 ## Draft Status
 
-This is a Stage S7b manuscript draft. The core numerical claims passed S7 data integrity review, and provisional references have been replaced with a verified Vancouver-style reference list. This draft is suitable for S8 reviewer-style critique, but it still requires target-journal formatting and table/figure insertion before submission.
+This is a Stage S8b revised manuscript draft. It implements the S8 major-revision roadmap by inserting manuscript tables and figures, clarifying missingness and model degrees of freedom, updating the fasting-glucose sensitivity analysis with fasting subsample weights, and tightening selected contribution and interpretation language. It still requires final target-journal formatting before S9 finalization.
 
 ---
 
@@ -22,11 +22,11 @@
 
 ## Methods
 
-This cross-sectional study used public-use NHANES 2017-2018 interview, examination, and laboratory files. Adults aged 20 years or older who self-reported no prior diabetes diagnosis and had available HbA1c data were included. Pregnant participants were excluded. The primary outcome was HbA1c-defined undiagnosed diabetes, defined as HbA1c >=6.5% among participants who self-reported no diabetes diagnosis. Prediabetes was defined as HbA1c 5.7%-6.4%. A sensitivity definition used HbA1c >=6.5% or fasting plasma glucose >=126 mg/dL. Survey weights, strata, and primary sampling units were incorporated using the R `survey` package. Weighted prevalence estimates and survey-weighted logistic regression models were calculated.
+This cross-sectional study used public-use NHANES 2017-2018 interview, examination, and laboratory files. Adults aged 20 years or older who self-reported no prior diabetes diagnosis and had available HbA1c data were included. Pregnant participants were excluded. The primary outcome was HbA1c-defined undiagnosed diabetes, defined as HbA1c >=6.5% among participants who self-reported no diabetes diagnosis. Prediabetes was defined as HbA1c 5.7%-6.4%. A fasting-subsample sensitivity definition used HbA1c >=6.5% or fasting plasma glucose >=126 mg/dL. Survey weights, strata, and primary sampling units were incorporated using the R `survey` package. Weighted prevalence estimates and survey-weighted logistic regression models were calculated.
 
 ## Results
 
-The final analytic sample included 4,004 self-reported non-diabetic adults with available HbA1c data after excluding pregnant participants. The weighted prevalence of HbA1c-defined undiagnosed diabetes was 2.17% (95% CI, 1.74%-2.70%), and the weighted prevalence of HbA1c-defined prediabetes was 24.76% (95% CI, 22.63%-27.02%). When fasting plasma glucose was added to the outcome definition, the estimated prevalence of undiagnosed diabetes increased to 3.26% (95% CI, 2.66%-3.98%). Weighted prevalence was higher among participants with obesity than among those without obesity (4.08% vs 0.85%). In a parsimonious survey-weighted logistic model, waist circumference (OR per cm, 1.051; 95% CI, 1.030-1.073) and non-HDL cholesterol (OR per mg/dL, 1.016; 95% CI, 1.008-1.023) were associated with higher odds of HbA1c-defined undiagnosed diabetes. Compared with non-Hispanic White participants, non-Hispanic Asian participants (OR, 5.986; 95% CI, 1.859-19.276) and non-Hispanic Black participants (OR, 4.099; 95% CI, 1.334-12.600) had higher odds. Reporting any physical activity was associated with lower odds in direction, but the confidence interval included the null (OR, 0.478; 95% CI, 0.211-1.078).
+The final analytic sample included 4,004 self-reported non-diabetic adults with available HbA1c data after excluding pregnant participants. The weighted prevalence of HbA1c-defined undiagnosed diabetes was 2.17% (95% CI, 1.74%-2.70%), and the weighted prevalence of HbA1c-defined prediabetes was 24.76% (95% CI, 22.63%-27.02%). In the fasting subsample, the fasting-weighted prevalence increased from 1.84% (95% CI, 1.29%-2.62%) using HbA1c alone to 4.06% (95% CI, 3.12%-5.28%) using HbA1c or fasting plasma glucose. Weighted prevalence was higher among participants with obesity than among those without obesity (4.08% vs 0.85%). In a parsimonious survey-weighted logistic model, waist circumference (OR per cm, 1.051; 95% CI, 1.030-1.073) and non-HDL cholesterol (OR per mg/dL, 1.016; 95% CI, 1.008-1.023) were associated with higher odds of HbA1c-defined undiagnosed diabetes. Compared with non-Hispanic White participants, non-Hispanic Asian participants (OR, 5.986; 95% CI, 1.859-19.276) and non-Hispanic Black participants (OR, 4.099; 95% CI, 1.334-12.600) had higher odds. Reporting any physical activity was associated with lower odds in direction, but the confidence interval included the null (OR, 0.478; 95% CI, 0.211-1.078).
 
 ## Conclusions
 
@@ -52,11 +52,11 @@
 
 Lifestyle variables, including physical activity, smoking, and sleep duration, may be related to diabetes risk and detection patterns, but their interpretation in cross-sectional survey data is complex. Participants with undiagnosed diabetes may have altered lifestyle behaviors, unmeasured comorbidities, or differential health awareness. Therefore, lifestyle factors in this study are treated as correlates rather than causal exposures. The analysis emphasizes descriptive patterning and adjusted associations, with cautious interpretation of variables whose confidence intervals are wide.
 
-The objective of this study was to estimate the weighted prevalence of HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults and to examine its demographic, anthropometric, cardiometabolic, and lifestyle correlates using NHANES 2017-2018 data. The study further evaluated HbA1c-defined prediabetes and a sensitivity definition that incorporated fasting plasma glucose. The central premise is that a screening gap can be described using routine survey measures, while the conclusions must remain bounded by the cross-sectional design and the limitations of single-measure laboratory definitions.
+The objective of this study was to estimate the weighted prevalence of HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults and to examine its demographic, anthropometric, cardiometabolic, and lifestyle correlates using NHANES 2017-2018 data. The study further evaluated HbA1c-defined prediabetes and a fasting-subsample sensitivity definition that incorporated fasting plasma glucose. The central premise is that a screening gap can be described using routine survey measures, while the conclusions must remain bounded by the cross-sectional design and the limitations of single-measure laboratory definitions.
 
 This focus differs from a conventional diabetes risk-factor analysis in two ways. First, the denominator is not the general adult population or adults with diagnosed diabetes, but adults who report no diabetes diagnosis. This restriction better matches the practical screening problem: clinicians and public health programs often need to decide which apparently non-diabetic adults may warrant laboratory testing or closer follow-up. Second, the analysis emphasizes routinely available correlates rather than complex prediction algorithms. Many recent studies apply prediction-oriented methods to diabetes classification, but the present study deliberately avoids presenting a clinical prediction model because the available data are cross-sectional, single-cycle, and not externally validated. A transparent, survey-weighted epidemiologic analysis is more appropriate for the current evidence base and is less likely to overstate clinical utility.
 
-The study also contributes by separating three related but distinct concepts: undiagnosed diabetes burden, cardiometabolic profile, and screening implications. Estimating prevalence describes the size of the screening gap. Comparing characteristics by outcome status describes the profile of adults who may be missed by self-report. Regression modeling evaluates whether selected measures remain associated after adjustment for major demographic factors. Keeping these aims distinct helps prevent overinterpretation. The analysis can identify associations that may guide future screening research, but it cannot determine whether modifying waist circumference, lipid levels, or physical activity would reduce undiagnosed diabetes in the observed population.
+The incremental contribution of this study is its deliberately parsimonious screening-gap profile for a recent pre-pandemic NHANES cycle: it separates undiagnosed diabetes burden, cardiometabolic profile, and screening implications in adults who self-report no diabetes diagnosis. Estimating prevalence describes the size of the screening gap. Comparing characteristics by outcome status describes the profile of adults who may be missed by self-report. Regression modeling evaluates whether selected measures remain associated after adjustment for major demographic factors. Keeping these aims distinct helps prevent overinterpretation. The analysis can identify associations that may guide future screening research, but it cannot determine whether modifying waist circumference, lipid levels, or physical activity would reduce undiagnosed diabetes in the observed population.
 
 # Methods
 
@@ -70,13 +70,13 @@
 
 The analytic population was restricted to adults aged 20 years or older. Participants were eligible for the primary analysis if they self-reported no prior diabetes diagnosis and had available HbA1c data. Diabetes self-report was derived from the NHANES diabetes questionnaire item asking whether a doctor or health professional had ever told the participant that they had diabetes. Participants who self-reported diagnosed diabetes were excluded from the primary analytic sample because the research question focused on laboratory-defined diabetes-range HbA1c among people who reported no diabetes diagnosis.
 
-Pregnant participants were excluded where pregnancy status was available because pregnancy can alter glycemic interpretation and because gestational diabetes is conceptually distinct from the nonpregnant adult diabetes screening question. The sample selection proceeded as follows: 9,254 NHANES 2017-2018 interview participants were available; 5,569 were aged 20 years or older; 4,517 adults self-reported no diabetes; 4,051 self-reported no diabetes and had available HbA1c data; and 4,004 remained after excluding pregnant participants. This final group constituted the primary analytic sample.
+Pregnant participants were excluded where pregnancy status was available because pregnancy can alter glycemic interpretation and because gestational diabetes is conceptually distinct from the nonpregnant adult diabetes screening question. The primary analytic sample included 4,004 participants. The final waist-circumference model included 3,621 participants after excluding observations with missing model covariates; the BMI and categorical sensitivity models included 3,707 participants. Key covariate missingness included waist circumference n=188, non-HDL cholesterol n=72, mean systolic blood pressure n=190, and physical activity n=0. The sample selection proceeded as follows: 9,254 NHANES 2017-2018 interview participants were available; 5,569 were aged 20 years or older; 4,517 adults self-reported no diabetes; 4,051 self-reported no diabetes and had available HbA1c data; and 4,004 remained after excluding pregnant participants. This final group constituted the primary analytic sample.
 
 ## Outcome definitions
 
 The primary outcome was HbA1c-defined undiagnosed diabetes, defined as HbA1c >=6.5% among participants who self-reported no prior diabetes diagnosis. Participants who self-reported no diabetes and had HbA1c <6.5% were classified as not having HbA1c-defined undiagnosed diabetes for the primary binary outcome. HbA1c-defined prediabetes was defined as HbA1c 5.7%-6.4% among the same self-reported non-diabetic population.
 
-A sensitivity definition of undiagnosed diabetes incorporated fasting plasma glucose. Participants were classified as having HbA1c- or fasting-glucose-defined undiagnosed diabetes if HbA1c was >=6.5% or fasting plasma glucose was >=126 mg/dL. Because fasting glucose data were available for a smaller subsample, this definition was treated as a sensitivity analysis rather than the primary outcome. The diagnostic thresholds were based on ADA and NIDDK criteria [5,6], but the study language treats these measures as epidemiologic definitions rather than clinical diagnoses because confirmatory testing was not available.
+A sensitivity definition of undiagnosed diabetes incorporated fasting plasma glucose. Participants were classified as having HbA1c- or fasting-glucose-defined undiagnosed diabetes if HbA1c was >=6.5% or fasting plasma glucose was >=126 mg/dL. Because fasting glucose data were available only for the fasting subsample, this definition was treated as a sensitivity analysis using fasting subsample weights (`WTSAF2YR`) rather than the primary outcome. The diagnostic thresholds were based on ADA and NIDDK criteria [5,6], but the study language treats these measures as epidemiologic definitions rather than clinical diagnoses because confirmatory testing was not available.
 
 ## Covariates
 
@@ -92,11 +92,11 @@
 
 ## Statistical analysis
 
-All analyses accounted for the NHANES complex sampling design. MEC examination weights (`WTMEC2YR`) were used because the primary outcome relied on examination and laboratory measures. Survey strata (`SDMVSTRA`) and primary sampling units (`SDMVPSU`) were incorporated. Analyses were conducted in R version 4.5.1 using the `survey` package version 4.5. The `survey.lonely.psu` option was set to adjust lonely primary sampling units.
+All analyses accounted for the NHANES complex sampling design. MEC examination weights (`WTMEC2YR`) were used because the primary outcome relied on examination and laboratory measures. Survey strata (`SDMVSTRA`) and primary sampling units (`SDMVPSU`) were incorporated. Analyses were conducted in R version 4.5.1 using the `survey` package version 4.5. The `survey.lonely.psu` option was set to adjust lonely primary sampling units. The final survey design had 15 design degrees of freedom; model parsimony was therefore prioritized over a broad covariate set.
 
 Weighted prevalence estimates and 95% confidence intervals were calculated for HbA1c-defined undiagnosed diabetes and HbA1c-defined prediabetes. Subgroup prevalence estimates were calculated by sex, age group, race/ethnicity, and obesity status. Weighted descriptive characteristics were summarized by undiagnosed diabetes status using survey-weighted means for continuous variables and survey-weighted percentages for binary variables.
 
-Survey-weighted logistic regression was used to estimate associations with HbA1c-defined undiagnosed diabetes. The final primary model was parsimonious and included age, sex, race/ethnicity, waist circumference, mean systolic blood pressure, non-HDL cholesterol, and any reported physical activity. This model was selected after a fuller model was found to be parameter-heavy relative to the design degrees of freedom in a single NHANES cycle. Two sensitivity models were generated: a BMI alternative model and a categorical screening model including obesity, measured hypertension, non-HDL cholesterol, and any reported physical activity. Odds ratios (ORs) and 95% confidence intervals (CIs) are reported. Because the analysis was exploratory and cross-sectional, emphasis was placed on effect estimates and interval precision rather than binary significance claims.
+Survey-weighted logistic regression was used to estimate associations with HbA1c-defined undiagnosed diabetes. The final primary model was parsimonious and included age, sex, race/ethnicity, waist circumference, mean systolic blood pressure, non-HDL cholesterol, and any reported physical activity. This model was selected after a fuller model was found to be parameter-heavy relative to the design degrees of freedom in a single NHANES cycle. Two sensitivity models were generated: a BMI alternative model and a categorical screening model including obesity, measured hypertension, non-HDL cholesterol, and any reported physical activity. A fasting-weighted sensitivity prevalence analysis used `WTSAF2YR` among participants with fasting glucose data. Odds ratios (ORs) and 95% confidence intervals (CIs) are reported. Because the analysis was exploratory and cross-sectional, emphasis was placed on effect estimates and interval precision rather than binary significance claims.
 
 # Results
 
@@ -110,7 +110,7 @@
 
 Among self-reported non-diabetic adults with available HbA1c data, 150 participants had HbA1c >=6.5%. The weighted prevalence of HbA1c-defined undiagnosed diabetes was 2.17% (95% CI, 1.74%-2.70%). HbA1c-defined prediabetes was more common: 1,254 participants had HbA1c 5.7%-6.4%, corresponding to a weighted prevalence of 24.76% (95% CI, 22.63%-27.02%).
 
-The sensitivity definition incorporating fasting plasma glucose identified 211 cases of HbA1c- or fasting-glucose-defined undiagnosed diabetes. The corresponding weighted prevalence was 3.26% (95% CI, 2.66%-3.98%). The higher prevalence under this definition is consistent with the expectation that HbA1c and fasting plasma glucose do not classify all participants identically. Because fasting glucose was available for a smaller subsample, the combined definition was retained as a sensitivity analysis rather than replacing the primary HbA1c-based definition.
+In the fasting subsample, the sensitivity definition incorporating fasting plasma glucose identified 115 cases of HbA1c- or fasting-glucose-defined undiagnosed diabetes among 1,807 participants. The corresponding fasting-weighted prevalence was 4.06% (95% CI, 3.12%-5.28%). The higher prevalence under this definition is consistent with the expectation that HbA1c and fasting plasma glucose do not classify all participants identically. Because fasting glucose was available for a smaller subsample, the combined definition was retained as a sensitivity analysis rather than replacing the primary HbA1c-based definition.
 
 ## Subgroup prevalence patterns
 
@@ -144,7 +144,7 @@
 
 ## Principal findings
 
-In this nationally representative cross-sectional analysis of self-reported non-diabetic U.S. adults in NHANES 2017-2018, HbA1c-defined undiagnosed diabetes was present in 2.17% of the weighted analytic population. HbA1c-defined prediabetes was substantially more common, affecting nearly one-quarter of the weighted analytic population. When fasting plasma glucose was added to the definition, the estimated prevalence of undiagnosed diabetes increased to 3.26%. These estimates demonstrate that self-reported absence of diabetes does not eliminate the possibility of diabetes-range laboratory values.
+In this nationally representative cross-sectional analysis of self-reported non-diabetic U.S. adults in NHANES 2017-2018, HbA1c-defined undiagnosed diabetes was present in 2.17% of the weighted analytic population. HbA1c-defined prediabetes was substantially more common, affecting nearly one-quarter of the weighted analytic population. In the fasting subsample, adding fasting plasma glucose increased the fasting-weighted estimate to 4.06%. These estimates demonstrate that self-reported absence of diabetes does not eliminate the possibility of diabetes-range laboratory values.
 
 The study also identified a cardiometabolic profile associated with HbA1c-defined undiagnosed diabetes. Participants with undiagnosed diabetes had higher weighted mean BMI, waist circumference, systolic blood pressure, total cholesterol, and non-HDL cholesterol, and lower HDL cholesterol than participants without undiagnosed diabetes. In survey-weighted logistic models, waist circumference and non-HDL cholesterol remained associated with higher odds of undiagnosed diabetes. Obesity and BMI were also associated with higher odds in sensitivity models. These findings indicate that routine anthropometric and lipid measures may help characterize screening gaps among adults who self-report no diabetes diagnosis.
 
@@ -160,7 +160,7 @@
 
 The lower primary prevalence estimate in this study should not be interpreted as evidence that undiagnosed diabetes is unimportant. A weighted prevalence near 2% among self-reported non-diabetic adults still represents a meaningful public health signal, especially because the same analytic population had a much larger burden of HbA1c-defined prediabetes. The prediabetes estimate is relevant because people in this range may not have symptoms and may not be aware of their glycemic status. Public health objectives such as Healthy People 2030 explicitly track undiagnosed prediabetes awareness [8], reflecting the view that earlier identification is part of chronic disease prevention. The current findings therefore fit within a broader prevention continuum rather than a narrow disease-detection frame.
 
-The sensitivity analysis also illustrates why surveillance studies should report definitions transparently. HbA1c-only and HbA1c-or-fasting-glucose definitions do not identify identical populations. In this study, incorporating fasting glucose increased the estimated weighted prevalence from 2.17% to 3.26%. That shift is large enough to matter for interpretation, but not so large that it undermines the primary analysis. Instead, it shows that HbA1c-defined undiagnosed diabetes is a conservative and reproducible main definition, while broader laboratory definitions may capture additional adults with dysglycemia.
+The sensitivity analysis also illustrates why surveillance studies should report definitions transparently. HbA1c-only and HbA1c-or-fasting-glucose definitions do not identify identical populations. In the fasting subsample, incorporating fasting glucose increased the fasting-weighted estimate from 1.84% to 4.06%. That shift is large enough to matter for interpretation, but not so large that it undermines the primary analysis. Instead, it shows that HbA1c-defined undiagnosed diabetes is a conservative and reproducible main definition, while broader laboratory definitions may capture additional adults with dysglycemia.
 
 ## Anthropometric measures and screening relevance
 
@@ -184,7 +184,7 @@
 
 The higher odds observed among non-Hispanic Asian and non-Hispanic Black participants require careful interpretation. Race and ethnicity in NHANES are social categories shaped by ancestry, culture, structural conditions, health care access, discrimination, environment, and measurement practices. They should not be interpreted as direct biological causes. In the context of undiagnosed diabetes, higher prevalence or odds may reflect differences in screening opportunities, health insurance, access to primary care, risk factor distributions, body composition, or thresholds at which glycemic abnormalities emerge.
 
-The finding among non-Hispanic Asian participants is particularly important because prior NHANES analyses have reported a relatively high proportion of undiagnosed diabetes among Asian American adults [9,10]. However, this study did not test ethnicity-specific BMI or waist thresholds, nor did it disaggregate Asian subgroups. The broad non-Hispanic Asian category may mask substantial heterogeneity. Similarly, the higher odds among non-Hispanic Black participants may reflect a combination of cardiometabolic risk, access to care, structural inequities, and diagnostic opportunities. Future studies with larger samples and more detailed social and health care access measures are needed to clarify these patterns.
+The finding among non-Hispanic Asian participants is particularly important because prior NHANES analyses have reported a relatively high proportion of undiagnosed diabetes among Asian American adults [9,10]. However, this study did not test ethnicity-specific BMI or waist thresholds, nor did it disaggregate Asian subgroups. The broad non-Hispanic Asian category may mask substantial heterogeneity. Similarly, the higher odds among non-Hispanic Black participants may reflect a combination of cardiometabolic risk, access to care, structural inequities, and diagnostic opportunities. Prior studies have reported racial and ethnic differences in cardiometabolic risk among adults with undiagnosed diabetes and gaps between guideline-based screening eligibility and actual screening behavior [18,19]. Future studies with larger samples and more detailed social and health care access measures are needed to clarify these patterns.
 
 In the manuscript, these findings should be presented as evidence that screening gaps are unevenly distributed. The discussion should connect them to public health screening equity rather than assigning inherent risk to racial or ethnic groups.
 
@@ -230,42 +230,68 @@
 
 # Conclusion
 
-Among self-reported non-diabetic U.S. adults in NHANES 2017-2018, HbA1c-defined undiagnosed diabetes affected 2.17% of the weighted analytic population, while HbA1c-defined prediabetes affected nearly one-quarter. A broader HbA1c or fasting glucose definition yielded a higher undiagnosed diabetes estimate. Waist circumference and non-HDL cholesterol were associated with higher odds of HbA1c-defined undiagnosed diabetes, and higher prevalence was observed among adults with obesity and in several race/ethnicity subgroups. These results suggest that routine anthropometric and lipid measures may help characterize diabetes screening gaps among adults who report no prior diabetes diagnosis. The findings should be interpreted as cross-sectional associations and require confirmation in studies with repeated testing, richer clinical covariates, and longitudinal follow-up.
-
----
-
-# Tables and Figures To Be Inserted
+Among self-reported non-diabetic U.S. adults in NHANES 2017-2018, HbA1c-defined undiagnosed diabetes affected 2.17% of the weighted analytic population, while HbA1c-defined prediabetes affected nearly one-quarter. A fasting-subsample HbA1c or fasting glucose definition yielded a higher undiagnosed diabetes estimate. Waist circumference and non-HDL cholesterol were associated with higher odds of HbA1c-defined undiagnosed diabetes, and higher prevalence was observed among adults with obesity and in several race/ethnicity subgroups. These results suggest that routine anthropometric and lipid measures may help characterize diabetes screening gaps among adults who report no prior diabetes diagnosis. The findings should be interpreted as cross-sectional associations and require confirmation in studies with repeated testing, richer clinical covariates, and longitudinal follow-up.
+
+---
+
+# Tables and Figures
 
 ## Figure 1
 
-Flow diagram of study population selection.
-
-Source file: `results/S3/flow_counts.csv`
+Study population selection. File: `results/S8b/figure1_flow.png`.
 
 ## Figure 2
 
-Weighted prevalence of HbA1c-defined undiagnosed diabetes by sex, age group, race/ethnicity, and obesity status.
-
-Source file: `results/S3/weighted_prevalence_subgroups.csv`
+Weighted prevalence of HbA1c-defined undiagnosed diabetes by subgroup. File: `results/S8b/figure2_subgroup_prevalence.png`.
 
 ## Table 1
 
-Weighted characteristics of self-reported non-diabetic adults by HbA1c-defined undiagnosed diabetes status.
-
-Source file: `results/S3/table1_weighted_by_outcome.csv`
+Weighted characteristics of self-reported non-diabetic adults by HbA1c-defined undiagnosed diabetes status. Values are weighted mean (SE) or weighted percent (SE).
+
+| Characteristic | No HbA1c-defined undiagnosed diabetes | HbA1c-defined undiagnosed diabetes | Missing, n |
+| --- | --- | --- | --- |
+| Age, years | 46.51 (0.57) | 54.71 (1.83) | 0 |
+| Obesity, % | 38.8% (1.8) | 75.8% (3.4) | 57 |
+| BMI, kg/m2 | 29.16 (0.22) | 35.07 (0.45) | 57 |
+| Waist circumference, cm | 98.94 (0.66) | 112.89 (1.25) | 188 |
+| Mean systolic BP, mmHg | 122.39 (0.52) | 135.90 (3.16) | 190 |
+| Mean diastolic BP, mmHg | 72.89 (0.58) | 77.05 (1.83) | 196 |
+| HbA1c, % | 5.42 (0.01) | 7.50 (0.22) | 0 |
+| Total cholesterol, mg/dL | 190.32 (1.61) | 211.39 (4.87) | 72 |
+| HDL cholesterol, mg/dL | 54.75 (0.54) | 46.53 (1.14) | 72 |
+| Non-HDL cholesterol, mg/dL | 135.56 (1.66) | 164.85 (4.87) | 72 |
+| Current smoker, % | 18.2% (1.2) | 14.8% (6.7) | 0 |
+| Short sleep <7h, % | 24.8% (1.5) | 30.2% (6.4) | 31 |
+| Any reported physical activity, % | 81.0% (0.9) | 56.1% (7.0) | 0 |
 
 ## Table 2
 
-Survey-weighted logistic regression for HbA1c-defined undiagnosed diabetes.
-
-Source file: `results/S3b/table2_final_main_waist_model.csv`
+Survey-weighted logistic regression for HbA1c-defined undiagnosed diabetes. Main waist-circumference model.
+
+| Variable | OR (95% CI) | Design df | Model n |
+| --- | --- | --- | --- |
+| Age, per year | 1.025 (0.983-1.068) | 15 | 3621 |
+| Female vs male | 1.861 (0.728-4.756) | 15 | 3621 |
+| Mexican American vs Non-Hispanic White | 3.072 (0.608-15.538) | 15 | 3621 |
+| Non-Hispanic Asian vs Non-Hispanic White | 5.986 (1.859-19.276) | 15 | 3621 |
+| Non-Hispanic Black vs Non-Hispanic White | 4.099 (1.334-12.600) | 15 | 3621 |
+| Other Hispanic vs Non-Hispanic White | 3.737 (0.665-20.989) | 15 | 3621 |
+| Other/Multiracial vs Non-Hispanic White | 1.774 (0.390-8.077) | 15 | 3621 |
+| Waist circumference, per cm | 1.051 (1.030-1.073) | 15 | 3621 |
+| Mean systolic BP, per mmHg | 1.012 (0.985-1.040) | 15 | 3621 |
+| Non-HDL cholesterol, per mg/dL | 1.016 (1.008-1.023) | 15 | 3621 |
+| Any reported physical activity vs none | 0.478 (0.211-1.078) | 15 | 3621 |
 
 ## Supplementary Tables
 
-- Supplementary Table 1: Variable definitions.
-- Supplementary Table 2: BMI alternative model.
-- Supplementary Table 3: Categorical screening model.
-- Supplementary Table 4: HbA1c/FPG sensitivity prevalence.
+- Supplementary Table 1: BMI alternative model (`results/S8b/supplementary_table_bmi_model.md`).
+
+- Supplementary Table 2: categorical screening model (`results/S8b/supplementary_table_categorical_model.md`).
+
+- Supplementary Table 3: fasting-weighted HbA1c/FPG sensitivity prevalence (`results/S8b/supplementary_table_fasting_sensitivity.md`).
+
+- Supplementary Table 4: covariate missingness (`results/S8b/covariate_missingness.md`).
+
 
 ---
 
@@ -288,6 +314,8 @@
 15. Tan MY, Weng L, Yang ZH, Zhu SX, Wu S, Su JH. The association between non-high-density lipoprotein cholesterol to high-density lipoprotein cholesterol ratio with type 2 diabetes mellitus: recent findings from NHANES 2007-2018. Lipids Health Dis. 2024;23(1):151. doi:10.1186/s12944-024-02143-8
 16. Seo IH, Son DH, Lee HS, Lee YJ. Non-HDL cholesterol as a predictor for incident type 2 diabetes in community-dwelling adults: longitudinal findings over 12 years. Transl Res. 2022;243:52-59. doi:10.1016/j.trsl.2021.12.008
 17. Ley SH, Harris SB, Connelly PW, Mamakeesick M, Gittelsohn J, Wolever TM, Hegele RA, Zinman B, Hanley AJ. Utility of non-high-density lipoprotein cholesterol in assessing incident type 2 diabetes risk. Diabetes Obes Metab. 2012;14(9):821-825. doi:10.1111/j.1463-1326.2012.01607.x
+18. Hunt KJ, Gebregziabher M, Egede LE. Racial and ethnic differences in cardio-metabolic risk in individuals with undiagnosed diabetes: National Health and Nutrition Examination Survey 1999-2008. J Gen Intern Med. 2012;27(8):893-900. doi:10.1007/s11606-012-2023-7
+19. Sheehy A, Pandhi N, Coursin DB, Flood GE, Kraft SA, Johnson HM, Smith MA. Minority status and diabetes screening in an ambulatory population. Diabetes Care. 2011;34(6):1289-1294. doi:10.2337/dc10-1785
 
 ---
 
@@ -295,12 +323,12 @@
 
 | Metric | Value |
 |---|---:|
-| Draft stage | S7b |
+| Draft stage | S8b |
 | Target word count | 6,500-8,500 |
-| Approximate current word count | 7,174 words by `wc -w` |
+| Approximate current word count | See `wc -w` after final formatting |
 | Sections completed | Abstract, Introduction, Methods, Results, Discussion, Conclusion |
 | Citation status | Verified Vancouver-style reference list; target-journal formatting still required |
-| Tables/figures inserted | Placeholders only |
+| Tables/figures inserted | Table 1, Table 2, Figure 1, Figure 2, and supplementary tables generated |
 
 ## Word Count by Section
 
@@ -312,3 +340,12 @@
 | Results | 1,100-1,400 | Complete |
 | Discussion | 2,200-2,700 | Complete |
 | Conclusion | 150-250 | Complete |
+
+
+# Data Availability
+
+NHANES 2017-2018 public-use files are available from CDC/NCHS. Analysis scripts and derived non-identifiable outputs for this project are stored in the local workflow directory under `artifacts/` and `results/`.
+
+# Ethics Statement
+
+This secondary analysis used publicly available, de-identified NHANES data. NHANES protocols are reviewed by the NCHS Research Ethics Review Board, and no additional participant contact occurred in this analysis.
```

## Machine Summary

```json
{
  "addedLineCount": 75,
  "removedLineCount": 37,
  "diffLineCount": 239,
  "addedHeadings": [
    "# S8b Revised Manuscript Draft",
    "# Tables and Figures",
    "# Data Availability",
    "# Ethics Statement"
  ],
  "removedHeadings": [
    "# S7b Draft: Citation-Clean English SCI Manuscript Draft",
    "# Tables and Figures To Be Inserted"
  ]
}
```
