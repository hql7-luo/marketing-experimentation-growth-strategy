# Hillstrom source and data audit

Verified on 2026-10-07 (America/Los_Angeles).

## Provenance and experimental design

Kevin Hillstrom published the challenge on March 20, 2008. The publisher describes 64,000 customers, randomized approximately equally into men's email, women's email, and no email, with outcomes tracked for two weeks. This supports experimental treatment comparisons; it does not establish an identifiable retailer, exact campaign date, modern applicability, or individual causal effects. [Original challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html)

The original page initially failed direct browser retrieval, but its publisher's Blogspot alias resolved to the complete original page. The author's May 4 follow-up independently links the same dataset and invites additional solutions. [Publisher follow-up](https://blog.minethatdata.com/2008/05/best-answer-e-mail-analytics-challenge.html)

A current academic paper treats Hillstrom as real-world experimental data. Its appendix correctly identifies `visit` as the outcome; its main-text word “purchase” for a 15.1% rate conflicts with that appendix and the original dictionary. Use the original field definitions. [Huang and Ascarza, Working Paper 24-034, Section 6 and Appendix E](https://www.hbs.edu/ris/Publication%20Files/24-034_73dcd8bc-6187-4c84-9a1f-5fc765b03181.pdf)

## Access and integrity

Downloaded directly from the [author's CSV URL](http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv) to `work/hillstrom-original.csv`.

- HTTP download succeeded. HTTPS attempts failed certificate validation in this environment; TLS verification was not disabled.
- Size: 3,964,977 bytes.
- SHA-256: `0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece`.
- Parsed records: 64,000; fields: 12; missing cells: 0.
- Exact arm counts: Mens E-Mail 21,307; Womens E-Mail 21,387; No E-Mail 21,306.

## Dictionary and observed values

These meanings follow the original publisher; the ranges and categories were independently checked in the downloaded CSV.

| Field | Meaning | Observed domain |
|---|---|---|
| recency | Prior-purchase age in months | 1–12 |
| history_segment | Prior-year spending band | 7 ordered bands |
| history | Prior-year dollars | 29.99–3,345.93 |
| mens / womens | Prior-year merchandise indicators | 0 / 1 |
| zip_code | Broad location category | Rural, Surburban, Urban |
| newbie | New in prior year | 0 / 1 |
| channel | Prior-year purchase channel | Phone, Web, Multichannel |
| segment | Randomized campaign arm | Three arms above |
| visit / conversion | Two-week site visit / purchase | 0 / 1 |
| spend | Two-week dollars | 0–499 |

The CSV spells the middle location category `Surburban`; normalize it to `Suburban` with a documented mapping. `mens` and `womens` describe purchases, not customer gender. Treatment and outcomes must never become targeting predictors.

There are 6,562 repeated complete records. With no customer identifier and coarse attributes, these may represent different customers. Keep all publisher rows; report identical-row counts without claiming confirmed duplicate customers. There are no names, addresses, emails, or customer IDs in the actual schema.

## Use and redistribution

The original publisher explicitly invites dataset analysis and public discussion of findings. Neither the original challenge nor the publisher follow-up reviewed here provides a named open-data license or an explicit grant to redistribute raw customer rows. Targeted publisher-domain searches did not produce such a grant. This is an unresolved permission boundary, not proof that permission cannot exist.

Keep raw and row-level derived data out of Git. Publish original analysis code, aggregate outputs, source attribution, download instructions, and this exact file checksum. Label any code license as applying to project code only. A mirror's MIT/BSD/CC declaration cannot establish the original publisher's data rights.

No external person was contacted, no request for permission was submitted, and no third-party account action was performed.
