"""
Seeds the `documents` table with a starter set of Indian legal source
snippets, and `cases` with a couple of sample judgments, so the API is
usable immediately after deploy. This is illustrative, not exhaustive —
replace/extend via POST /documents/upload or a real ingestion pipeline
(PDF parsing of full Acts, judgments, notifications) for production use.
"""
from sqlalchemy.orm import Session
from app import models

LEGAL_SEED = [
    ("Constitution of India", "Article 21", "Protection of life and personal liberty. No person shall be deprived of his life or personal liberty except according to procedure established by law.", "constitutional"),
    ("Constitution of India", "Article 19", "Guarantees six fundamental freedoms to citizens including freedom of speech and expression, assembly, association, movement, residence, and profession, subject to reasonable restrictions.", "constitutional"),
    ("Constitution of India", "Article 32", "Right to Constitutional Remedies. Allows citizens to move the Supreme Court directly for enforcement of fundamental rights.", "constitutional"),
    ("Bharatiya Nyaya Sanhita (BNS) 2023", "Section 103", "Punishment for murder — whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.", "criminal"),
    ("Bharatiya Nyaya Sanhita (BNS) 2023", "Section 85", "Husband or relative of husband subjecting a woman to cruelty is punishable with imprisonment up to three years and fine.", "criminal"),
    ("Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023", "Section 173", "Every information relating to commission of a cognizable offence, given orally or in writing, shall be recorded by the officer in charge of a police station (First Information Report).", "criminal-procedure"),
    ("Consumer Protection Act, 2019", "Section 2(7)", "Defines 'consumer' as a person who buys goods or hires services for consideration, but does not include a person who obtains goods for resale or commercial purpose.", "consumer"),
    ("Consumer Protection Act, 2019", "Section 35", "A complaint may be filed before the District Consumer Commission where the value of goods/services paid does not exceed one crore rupees.", "consumer"),
    ("Right to Information Act, 2005", "Section 6", "A citizen may request information by submitting an application to the Public Information Officer, in writing or electronically, with the prescribed fee.", "rti"),
    ("Right to Information Act, 2005", "Section 7", "The PIO must respond within 30 days of receipt of request; 48 hours where the information concerns life or liberty of a person.", "rti"),
    ("Information Technology Act, 2000", "Section 66C", "Punishment for identity theft — fraudulent or dishonest use of another person's electronic signature, password, or unique identification feature; imprisonment up to three years and fine up to one lakh rupees.", "cyber"),
    ("Information Technology Act, 2000", "Section 66E", "Punishment for violation of privacy — capturing, publishing, or transmitting images of a person's private area without consent; imprisonment up to three years or fine up to two lakh rupees, or both.", "cyber"),
    ("Motor Vehicles Act, 1988", "Section 166", "An application for compensation arising out of a motor vehicle accident may be made to the Claims Tribunal by the injured person or legal representatives of the deceased.", "motor-vehicles"),
    ("Motor Vehicles Act, 1988", "Section 185", "Driving under the influence of alcohol or drugs is punishable with imprisonment up to six months and/or fine, higher for repeat offences.", "motor-vehicles"),
    ("Indian Contract Act, 1872", "Section 10", "All agreements are contracts if made by free consent of parties competent to contract, for a lawful consideration and lawful object, and not expressly declared void.", "contract"),
    ("Indian Contract Act, 1872", "Section 73", "A party who suffers from breach of contract is entitled to compensation for loss or damage naturally arising in the usual course of things from the breach.", "contract"),
    ("Hindu Marriage Act, 1955", "Section 13", "Grounds on which either party to a marriage may present a petition for divorce, including cruelty, desertion for two years, and conversion of religion.", "family"),
    ("Companies Act, 2013", "Section 3", "A company may be formed for any lawful purpose by seven or more persons (public company) or two or more persons (private company) by subscribing their names to a memorandum.", "corporate"),
    ("Legal Services Authorities Act, 1987", "Section 12", "Sets out categories of persons entitled to free legal aid, including women, children, SC/ST members, industrial workmen, disabled persons, and those with annual income below the prescribed limit.", "legal-aid"),
    ("Aadhaar Act, 2016", "Section 3", "Every resident is entitled to obtain an Aadhaar number by submitting demographic and biometric information through the enrolment process; enrolment is currently voluntary for most purposes but required for specified benefits/services.", "government-id"),
    ("Aadhaar Act, 2016", "Section 4", "An Aadhaar number is proof of identity, subject to authentication; it is not proof of citizenship or domicile and does not by itself confer any right to Indian citizenship.", "government-id"),
    ("Aadhaar Act, 2016", "Section 7", "The government may require Aadhaar authentication as a condition for receipt of a subsidy, benefit, or service funded from the Consolidated Fund of India.", "government-id"),
    ("Income-tax Act, 1961", "Section 139A", "Every person whose total income exceeds the taxable limit, who carries on business/profession with turnover above the prescribed threshold, or who enters into specified high-value transactions, must apply for a Permanent Account Number (PAN); PAN must be quoted on income tax returns and specified financial documents.", "government-id"),
    ("Income-tax Act, 1961", "Section 139A(5)", "PAN must be quoted in specified transactions such as opening a bank account, property purchase above prescribed value, and other transactions notified by the government.", "government-id"),
    ("Passports Act, 1967", "Section 6", "Sets out grounds on which passport issuance may be refused, including pending criminal proceedings, prior conviction for certain offences, or where issuance would be prejudicial to India's sovereignty and security.", "government-id"),
    ("Central Goods and Services Tax Act, 2017", "Section 22", "Every supplier is liable to be registered under GST in the State/UT from which taxable supply is made if aggregate turnover in a financial year exceeds the prescribed threshold (currently ₹40 lakh for goods, ₹20 lakh for services in most states, lower for special category states).", "taxation"),
    ("National Food Security Act, 2013", "Section 3", "Eligible households are entitled to receive foodgrains at subsidized prices under the Targeted Public Distribution System (TPDS), identified as either 'priority' households or 'Antyodaya' (poorest of the poor) households by the state government.", "government-id"),
]

CASE_SEED = [
    (
        "Justice K.S. Puttaswamy (Retd.) v. Union of India",
        "Supreme Court of India", "9-judge bench", 2017,
        "(2017) 10 SCC 1",
        "Held that the right to privacy is a fundamental right protected under Article 21 of the Constitution.",
        ["Constitution of India"],
    ),
    (
        "M.C. Mehta v. Union of India",
        "Supreme Court of India", "Bhagwati, J.", 1987,
        "1987 AIR 1086",
        "Landmark environmental law case establishing the principle of absolute liability for hazardous industries.",
        ["Constitution of India"],
    ),
]


def seed_if_empty(db: Session):
    if db.query(models.LegalDocument).count() == 0:
        for act_name, section, content, category in LEGAL_SEED:
            db.add(models.LegalDocument(act_name=act_name, section=section, content=content, category=category))
        db.commit()

    if db.query(models.Case).count() == 0:
        for title, court, judge, year, citation, summary, related_acts in CASE_SEED:
            db.add(models.Case(
                title=title, court=court, judge=judge, year=year,
                citation=citation, summary=summary, related_acts=related_acts,
            ))
        db.commit()
