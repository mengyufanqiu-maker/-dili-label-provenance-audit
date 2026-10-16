# SUBMISSION_CHECKLIST — Computational Toxicology 投稿清单

稿件：`submission/manuscript.docx`（由 `DILI_LABEL_STABILITY_DATA_NOTE_v0.5.md` 生成，3 张 Word 表格）
SI：`submission/supplementary_information.docx`（Table S1）
图：`figures/fig1_reclassification_directions.png`、`fig2_cross_source_filtering.png`（300 dpi）
Cover letter 草稿：`submission/cover_letter_draft.md`（**本机保存，勿上传公开仓库**——含个人邮箱）

## 投稿前必做（作者本人）

1. ~~补作者信息块~~ **已完成**：Yu Zhang，Clinical Pharmacy Program, School of Pharmacy, Anhui Medical University, Hefei, Anhui, China；通讯邮箱 mengyufanqiu@gmail.com。投稿前由作者最终确认署名与作者顺序（单一作者）。
2. **核对官方 Guide for Authors**（投稿系统内也会显示）：确认稿件类型（Original research 还是 Short Communication——若后者存在且篇幅合适则优先）与字数限制；摘要结构已按 Background/Methods/Results/Conclusions 写好，可直接用。
3. **AI 使用披露**（Elsevier 2026 政策：实质性参与稿件准备的生成式 AI 须披露；参与研究设计/方法/解释的还应在正文 Methods 说明——正文已加 "Generative AI use" 段）。提交系统粘贴版：
   > "Generative AI tools were used in the preparation of this manuscript: ChatGPT (OpenAI) for research positioning, literature discussion, and iterative review and revision; Claude (Anthropic) for drafting and revising the text and for generating and debugging the reproduction and analysis code. All data, numerical results, and analyses were produced and verified by the author's own scripts against local data and public sources; every claim in the final manuscript was verified by the author, who takes full responsibility for the content. No generative-AI output was used as a source of data or as a claim of fact without author verification."
4. **利益冲突**：声明无（如无）；**资助**：无（如无）；**伦理**：本研究仅使用公开数据集与已发表数据，不涉及人类受试者/动物，无需伦理审批——在系统相应栏填写。
5. **推荐审稿人**：3–5 名，可从参考文献作者中选（如 Seal S、Thakkar S、Chen M、Tong W 等），须由作者在投稿系统填写其单位邮箱（我不能替你编造邮箱，须你从 PubMed 核实）。
6. **上传顺序**（Editorial Manager）：Manuscript（docx）→ Supplementary（docx）→ Figures（2 PNG）→ Cover letter → 其余声明。
7. 注册/登录 Editorial Manager（Elsevier 统一入口 → 选 Computational Toxicology）→ 逐步填写 → 最终确认页**由你本人核对后提交**。

## 已就绪（无需再动）

- 正文：v1.0（七轮外部审稿修订后，投稿干净版）；数据可用性含公开仓库 URL ✓
- 公开仓库：https://github.com/mengyufanqiu-maker/-dili-label-provenance-audit（脚本 + 输出 + 清单 + 图）✓
- 参考文献：9 条，DOI/PMID 已核（作者列表按期刊格式投前再过一遍即可；Elsevier 首投 YPW 政策接受任意一致格式）

## 风险提示（诚实）

- 录用不可预测；本清单只保证"提交合规"，不保证结果。
- 若编辑部 desk-reject 理由为"稿件类型不符"，Plan B：转投 J. Cheminformatics Data note（结构需小幅调整，我可以做）。

## Guide for Authors 合规核对（2026-10-17，官方指南 PDF 已读）

- **稿件类型**：现行指南只列 4 类（原创机制研究论文 / 综述 / 致编辑来信 / 公告）。**无 Short Communication**。→ EM 中选择 **Original research paper**；范围条款"毒理学大数据：集成、管理与分析"是本文的适配依据（4,813 词正文在原创论文范围内）。
- **摘要 ≤250 词**：已压至 **237 词** ✓。
- **关键词 1–7 个**：已加（drug-induced liver injury; benchmark; label provenance; DILIrank; DILIst; ambiguous; data curation）✓。
- **Highlights**：3–5 条 × ≤85 字符，独立可编辑文件，文件名含 "highlights" → `submission/highlights.txt`（5 条已备）✓；上传时文件名可改为 highlights.docx。
- **图形摘要**：可选（建议提供）——可在投稿时跳过、修改阶段再补，或现在用 Figure 1 改做。
- **GenAI 声明**：必须为参考文献前的新章节，标题与模板句式已按期刊要求改好 ✓（正文 + declarations.docx 双份）。
- **声明独立文件**：`submission/declarations.docx`（COI/资助/伦理/AI），在 EM 的 "Additional/upload files" 步骤上传 ✓。
- **CRediT 作者贡献**：EM 中按单作者填：Conceptualization; Data curation; Formal analysis; Investigation; Methodology; Software; Validation; Visualization; Writing – original draft; Writing – review and editing。
- **图规格**：300 dpi，整页最小宽 2244 px → 已重生成 **2265 px** ✓；每图独立文件、正文引用 ✓；彩色图无障碍要求已满足（调色板经 CVD 验证）。
- **表**：可编辑 Word 表格（非图片）✓；正文全部引用 ✓；编号按出现顺序 ✓。
- **引用格式**：指南允许首投任意一致格式（期刊样式在排版阶段应用）→ 当前编号体系无需改动。
- **数据链接**：EM 提交时在数据提示处粘贴公开仓库 URL（https://github.com/mengyufanqiu-maker/-dili-label-provenance-audit）。
- **通讯作者**：标题页已标注 "Corresponding author: Yu Zhang, mengyufanqiu@gmail.com" ✓；出版协议资格基于通讯作者单位。

