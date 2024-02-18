# CaluxPy Extraction Tool

## Project Description

Python package for Fixed Income Valuation and Analysis ranging from individual assets to multiple assets, Modern
Portfolio Theory and some basics of Issuance Risk Management. It is important to note that this covers both couponed
and zero-coupon bonds. 

## Table of Contents
- [Payment Types Covered](#payment-types-covered)
- [Methodologies of Valuation Covered](#methodologies-for-the-calculation-of-cash-flows-coupons-covered)
- [Main Features and Functions](#main-features-and-functions)
- [Dependencies](#dependencies)
- [Where to get it](#where-to-get-it)
- Documentation

## Payment Types Covered

- **Bullet Payment:** this kind of repayment is a lump sum payment made for the entirety of an outstanding loan amount, usually at maturity.
- **Amortized:** in this kind of payment the issuer amortizes in previously scheduled dates x pertentage of the outstanding amount in t period of time with could have the same periodicity as the coupons, but should be paid with the coupons, i.e. the coupon peiodicity could be semi-anually and the amortization could be anually; both periodicities are not the same but an amortization will be made on a coupon payment date and that should hold true. For the amortizations it would be needed the starting date, the amount of amortizations, the percentage of the outstanding amount to be amortized and the periodicity.
- **Payment in Kind (PiK):** this is the use of a good or service as payment instead of cash. Also refers to the payment of interest ot dividends to investors of bonds, notes, or preferred stock with additional securities or equity instead of cash. In the scope of this project, for earlier versions, the coupons, would be held and their interest would compound. As the amortized payments this will assume the a star date for the PiK payments and start holdind the cashflows.

## Methodologies for the calculation of Cash Flows (Coupons) Covered

- **ICMA:**
- **Actual/Actual:**
- **Actual/365:**
- **Actual/360:**
- **ISMA-360:**

## Main Features and Functions

- **Single Asset Calculator:**
- **Multiple Asset Calculator:**
- **Modern Portfolio Theory:**

## Dependencies
- [numpy](https://pypi.org/project/numpy/)
- [pandas](https://pypi.org/project/pandas/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [scipy](https://pypi.org/project/SciPy/)
- [pymongo](https://pypi.org/project/pymongo/)
- [pyodbc](https://pypi.org/project/pyodbc/)

## Where to get it
```
pip install caluxPy-ext
```


This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
