# LeadNest Performance Tracking Spreadsheet Template

**Google Sheets template to track trials, demos, conversions, and churn**

---

## 📊 Sheet Structure Overview

### Sheet Tabs:
1. **Dashboard** - Executive summary and key metrics
2. **Lead Tracking** - Prospects and outreach activities
3. **Trial Tracking** - Free trial users and conversion
4. **Customer Tracking** - Paid customers and subscription details
5. **Channel Performance** - Marketing channel effectiveness
6. **Financial Metrics** - Revenue, MRR, churn analysis
7. **Activity Log** - Daily activity tracking

---

## 📋 Sheet 1: Dashboard

### Key Metrics (Auto-calculated from other sheets):

```
=== LeadNest PERFORMANCE DASHBOARD ===

📊 OVERVIEW (This Month)
• Total Leads Generated: =COUNTIF('Lead Tracking'!B:B,">=1/1/2025")
• Trials Started: =COUNTIF('Trial Tracking'!C:C,">=1/1/2025")
• Demos Completed: =COUNTIF('Lead Tracking'!F:F,"Demo Completed")
• Paid Conversions: =COUNTIF('Customer Tracking'!D:D,">=1/1/2025")

💰 FINANCIAL
• Monthly Recurring Revenue: =SUM('Customer Tracking'!G:G)
• Average Revenue Per User: =AVERAGE('Customer Tracking'!G:G)
• Customer Lifetime Value: =H4*12 (assuming 12 month average)
• Total Revenue (All Time): =SUM('Financial Metrics'!C:C)

📈 CONVERSION RATES
• Lead to Demo Rate: =H5/H2
• Demo to Trial Rate: =H3/H5  
• Trial to Paid Rate: =H4/H3
• Overall Conversion Rate: =H4/H2

🎯 GROWTH METRICS
• New Customers This Month: =COUNTIF('Customer Tracking'!D:D,">=1/1/2025")
• Churned Customers This Month: =COUNTIF('Customer Tracking'!I:I,">=1/1/2025")
• Net Growth: =H13-H14
• Churn Rate: =H14/COUNTIF('Customer Tracking'!H:H,"Active")

📱 CHANNEL PERFORMANCE (Top 3)
• Facebook Groups: =COUNTIF('Channel Performance'!A:A,"Facebook")
• LinkedIn: =COUNTIF('Channel Performance'!A:A,"LinkedIn") 
• Reddit: =COUNTIF('Channel Performance'!A:A,"Reddit")
```

### Weekly Goals Tracker:
```
WEEK OF: [Date]
Goal: Actual: Status:
• Outreach Contacts: 100 | __ | __
• Demos Scheduled: 10 | __ | __
• Trials Started: 15 | __ | __
• Paid Conversions: 3 | __ | __
```

---

## 📋 Sheet 2: Lead Tracking

### Column Headers:
```
A: Contact Name
B: Company
C: Email
D: Phone
E: Source (Facebook/LinkedIn/Reddit/etc.)
F: Status (Cold/Contacted/Demo Scheduled/Trial/Customer/Dead)
G: First Contact Date
H: Last Contact Date
I: Demo Date
J: Demo Outcome
K: Trial Start Date
L: Conversion Date
M: Notes
N: Next Action
O: Next Action Date
```

### Sample Rows:
```
Mike Rodriguez | Rodriguez Roofing | mike@rodriguezroofing.com | 555-0123 | Facebook Groups | Demo Completed | 1/15/2025 | 1/18/2025 | 1/18/2025 | Started Trial | 1/18/2025 | | Very interested, asked about export limits | Follow up in 3 days | 1/21/2025

Sarah Chen | Elite Solar | sarah@elitesolar.net | 555-0456 | LinkedIn | Contacted | 1/16/2025 | 1/16/2025 | | | | | Replied asking for more info | Send demo link | 1/17/2025

Tommy Martinez | Tommy's HVAC | tommy@tommyshvac.com | 555-0789 | Reddit | Cold | 1/17/2025 | | | | | | Found in r/HVAC thread | Send initial DM | 1/18/2025
```

### Conditional Formatting Rules:
- **Green:** Status = "Customer"
- **Blue:** Status = "Trial" 
- **Yellow:** Status = "Demo Scheduled"
- **Orange:** Status = "Contacted"
- **Red:** Next Action Date is overdue

---

## 📋 Sheet 3: Trial Tracking

### Column Headers:
```
A: User Name
B: Email
C: Trial Start Date
D: Trial End Date
E: Source Lead
F: Usage Level (High/Medium/Low)
G: Searches Performed
H: Exports Downloaded
I: Trial Outcome (Converted/Churned/Extended)
J: Conversion Date
K: Plan Selected
L: Monthly Value
M: Conversion Notes
```

### Sample Rows:
```
Mike Rodriguez | mike@rodriguezroofing.com | 1/18/2025 | 1/25/2025 | Sarah Chen LinkedIn | High | 47 | 12 | Converted | 1/23/2025 | Professional | $49 | Loved the AI enrichment feature

Lisa Wang | lisa@wangplumbing.biz | 1/19/2025 | 1/26/2025 | Facebook Groups | Low | 3 | 0 | Churned | | | $0 | Never logged back in after signup

David Smith | dave@smithelectric.co | 1/20/2025 | 1/27/2025 | Reddit | Medium | 15 | 3 | | | | | Still in trial, engaged user
```

### Usage Level Criteria:
- **High:** 20+ searches OR 5+ exports
- **Medium:** 5-19 searches OR 1-4 exports  
- **Low:** <5 searches AND 0 exports

---

## 📋 Sheet 4: Customer Tracking

### Column Headers:
```
A: Customer Name
B: Company
C: Email
D: Signup Date
E: Plan Type
F: Billing Cycle
G: Monthly Value
H: Status (Active/Churned/Paused)
I: Churn Date
J: Churn Reason
K: Total Payments
L: Customer Success Score (1-10)
M: Renewal Date
N: Upsell Opportunities
O: Notes
```

### Sample Rows:
```
Mike Rodriguez | Rodriguez Roofing | mike@rodriguezroofing.com | 1/23/2025 | Professional | Monthly | $49 | Active | | | $49 | 9 | 2/23/2025 | Agency Plan | Super happy customer, referring others

Jane Foster | Foster Construction | jane@fosterconstruction.net | 1/15/2025 | Agency | Annual | $149 | Active | | | $1788 | 8 | 1/15/2026 | API Access | Uses it daily, great case study

Bob Wilson | Wilson Plumbing | bob@wilsonplumbing.org | 2/1/2025 | Professional | Monthly | $49 | Churned | 2/15/2025 | Price too high | $49 | 6 | | | Said would consider at $29/month
```

### Customer Health Scoring:
- **9-10:** Highly engaged, likely to renew and refer
- **7-8:** Satisfied, stable customer
- **5-6:** At risk, needs attention
- **1-4:** Likely to churn, immediate intervention needed

---

## 📋 Sheet 5: Channel Performance

### Column Headers:
```
A: Channel
B: Contact Date
C: Contact Name
D: Response Rate
E: Demo Rate
F: Trial Rate
G: Conversion Rate
H: Cost Per Lead
I: Time Investment (hours)
J: ROI
K: Notes
```

### Sample Data:
```
Facebook Groups | 1/15/2025 | Mike Rodriguez | 25% | 15% | 60% | 40% | $0 | 2.5 | High | Best performing channel
LinkedIn | 1/16/2025 | Sarah Chen | 35% | 20% | 50% | 30% | $0 | 3.0 | High | Professional audience
Reddit | 1/17/2025 | Tommy Martinez | 15% | 8% | 40% | 25% | $0 | 1.5 | Medium | Requires authentic engagement
Twitter | 1/18/2025 | Lisa Wang | 10% | 5% | 30% | 20% | $0 | 1.0 | Low | Good for brand building
Cold Email | 1/19/2025 | David Smith | 5% | 2% | 20% | 15% | $0 | 2.0 | Low | Low response rates
```

### Channel Formulas:
```
Response Rate = Responses / Contacts
Demo Rate = Demos / Responses  
Trial Rate = Trials / Demos
Conversion Rate = Customers / Trials
ROI = (Revenue Generated - Time Cost) / Time Cost
```

---

## 📋 Sheet 6: Financial Metrics

### Monthly Revenue Tracking:
```
A: Month
B: New Customers
C: New Revenue
D: Churned Customers
E: Lost Revenue
F: Net New Revenue
G: Total MRR
H: Growth Rate
I: Notes
```

### Sample Data:
```
Jan 2025 | 8 | $392 | 1 | $49 | $343 | $343 | -- | Launch month
Feb 2025 | 12 | $588 | 2 | $98 | $490 | $833 | 143% | Strong growth
Mar 2025 | 15 | $735 | 3 | $147 | $588 | $1,421 | 71% | Word of mouth kicking in
```

### Key Financial Formulas:
```
Growth Rate = (Current MRR - Previous MRR) / Previous MRR
Customer Acquisition Cost = Marketing Spend / New Customers
Customer Lifetime Value = Average Monthly Revenue / Churn Rate
Monthly Churn Rate = Churned Customers / Total Customers at Start of Month
```

### Revenue Projections:
```
Current MRR: =SUM('Customer Tracking'!G:G)
Projected 3-Month Revenue: =Current MRR * 3 * 1.2 (assuming 20% monthly growth)
Projected 6-Month Revenue: =Current MRR * 6 * 1.5 (assuming continued growth)
Projected Annual Revenue: =Current MRR * 12 * 2.0 (assuming doubling)
```

---

## 📋 Sheet 7: Activity Log

### Daily Activity Tracking:
```
A: Date
B: Facebook Group Posts
C: Facebook Comments
D: LinkedIn Connections
E: LinkedIn Messages
F: Reddit Comments
G: Twitter Engagements
H: Cold Emails
I: Total Touches
J: Demos Scheduled
K: Trials Started
L: Conversions
M: Notes
```

### Weekly Summary:
```
=== WEEK OF [Date] ===
Total Outreach: =SUM(I2:I8)
Demos Scheduled: =SUM(J2:J8)
Trials Started: =SUM(K2:K8)
Conversions: =SUM(L2:L8)

Activity Rate: =I9/5 (touches per day)
Demo Rate: =J9/I9 (demos per touch)
Conversion Rate: =L9/K9 (conversions per trial)
```

---

## 📊 Advanced Analytics & Formulas

### Cohort Analysis:
```
=== JANUARY 2025 COHORT ===
Month 1 Retention: =COUNTIFS('Customer Tracking'!D:D,">=1/1/2025",'Customer Tracking'!D:D,"<2/1/2025",'Customer Tracking'!H:H,"Active")/COUNTIFS('Customer Tracking'!D:D,">=1/1/2025",'Customer Tracking'!D:D,"<2/1/2025")

Month 2 Retention: [Similar formula for 2-month retention]
Month 3 Retention: [Similar formula for 3-month retention]
```

### Lead Scoring Model:
```
Lead Score = 
+ Source Score (Facebook: 10, LinkedIn: 8, Reddit: 6, Twitter: 4, Email: 2)
+ Engagement Score (Demo: 20, Trial: 15, Response: 10, View: 5)
+ Company Size Score (1-10 employees: 10, 11-50: 8, 51+: 6)
+ Response Time Score (Same day: 10, 1 day: 8, 2-3 days: 6, 4+ days: 3)
```

### Predictive Metrics:
```
Trial to Paid Prediction:
IF(AND(Searches>10, Exports>2, Days_Active>3), "Likely", "Unlikely")

Churn Risk Score:
IF(AND(Last_Login>7, Usage_Score<3, Support_Tickets>2), "High Risk", "Low Risk")
```

---

## 🎯 How to Use This Template

### Daily (5 minutes):
1. Log all outreach activity in Activity Log
2. Update Lead Tracking with new contacts and status changes
3. Check Dashboard for key metrics

### Weekly (15 minutes):
1. Review Channel Performance and adjust strategy
2. Analyze Trial Tracking for conversion patterns
3. Update Customer Success Scores
4. Plan next week's activities based on data

### Monthly (30 minutes):
1. Complete Financial Metrics analysis
2. Run cohort analysis on customer retention
3. Review and optimize underperforming channels
4. Set next month's goals based on trends

### Key Reports to Generate:
- **Weekly Channel Performance Report**
- **Monthly Revenue and Growth Report**  
- **Customer Health and Churn Analysis**
- **Lead Quality and Conversion Analysis**

**This spreadsheet turns your LeadNest launch from guesswork into data-driven growth! 📊**
