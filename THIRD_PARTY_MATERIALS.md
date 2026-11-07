# Third-party materials and separate rights

The repository contains materials with different copyright and licensing status. The MIT
license in `LICENSE` applies to the original audit software and project-authored audit
documentation. It does **not** replace, extend, or resolve rights in third-party source
materials.

This file records the current evidence; it is not legal advice.

## Published 2026 journal article

File:

`docs/A methodological approach to energy optimization for buildings by utilizing machine learning-based surrogate model and an optimization technique.pdf`

Bibliographic identification:

- Le Quang Huy and Hoang Quynh Anh, *A methodological approach to energy optimization for
  buildings by utilizing machine learning-based surrogate model and an optimization
  technique*.
- HCMCOUJS-Advances in Computational Structures, 16(1), 30–60.
- DOI: <https://doi.org/10.46223/HCMCOUJS.acs.en.16.1.84.2026>.
- SHA-256: `49a72ad4f46f58ff4257714e075e54926ffa039b1878c3fecd7dacff57ec174b`.

Journal page 60 states:

> © 2026 The Author(s). Published by HCMCOU Journal of Science - Advances in
> Computational Structures. This article is licensed under CC BY-NC 4.0.

The article is therefore treated separately under
[Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/),
not under MIT. Reuse must satisfy the applicable attribution, license-notice,
change-indication, and noncommercial conditions. The CC license must not be represented as
covering the audit software, and MIT must not be represented as relicensing the article.

Whether a planned repository release, manuscript, archive, service, or downstream use is
noncommercial and otherwise compliant must be assessed for that specific publication use.

## Historical 2023 source materials

The following historical source class is retained under `data/original/`:

- `Report_HuyQLe-QAnh 23-6.docx`;
- `building_data.csv`, `processed_data.csv`, and `output_values.csv`;
- `input_data.py` and `ML_model.py`.

No license or written redistribution authorization for these files has been established in
the reviewed evidence. Their presence in this repository, their use as audit evidence, and
the repository's MIT license do not establish permission to republish, sublicense, or reuse
them. Their rights status is `NOT_VERIFIABLE` pending evidence from the relevant rights
holders or another documented legal basis.

Before publication release, these files must either:

1. have documented permission or another reviewed legal basis for the intended use; or
2. be excluded/quarantined from the distributable publication artifact while preserving an
   auditable description and checksums where legally appropriate.

## Audit code and project-authored outputs

Subject to third-party content embedded or quoted within them, the original audit code,
tests, scripts, generated numerical results, and project-authored audit documentation are
provided under the repository's MIT license. This includes the implementation under
`src/itp_opt/`, verification scripts, and regression tests.

## Publication-release gate

Publication approval remains `HOLD` until all of the following are recorded:

- a complete material-level rights inventory;
- the disposition and redistribution basis for every historical source file;
- CC BY-NC 4.0 attribution and license compliance for the journal PDF and any reused
  article content, tables, or figures;
- an assessment that the intended use falls within the permitted noncommercial scope or
  separate permission has been obtained;
- confirmation that release packaging does not imply that MIT covers third-party works;
- retained evidence of permissions, exclusions, and attribution text.

Rights clearance is a substantive publication criterion, not an editorial formatting task.
