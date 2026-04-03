---
title: "Thread by @karpathy"
source: "https://x.com/karpathy/status/2039805659525644595"
author:
  - "[[@karpathy]]"
published: 2026-04-03
created: 2026-04-03
description:
tags:
  - "clippings"
---
**Andrej Karpathy** @karpathy [2026-04-02](https://x.com/karpathy/status/2039805659525644595)

LLM Knowledge Bases  
LLM 知识库  
  
Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest. In this way, a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating knowledge (stored as markdown and images). The latest LLMs are quite good at it. So:  
我最近发现非常有用的一点是：利用大型语言模型（LLM）来建立各种研究兴趣主题的个人知识库。这样一来，我最近的代币吞吐量中很大一部分减少了操作代码，而更多地用于处理知识（以标记和图像形式存储）。最新的大型语言模型在这方面做得相当不错。所以：  
  
Data ingest:

I index source documents (articles, papers, repos, datasets, images, etc.) into a raw/ directory, then I use an LLM to incrementally "compile" a wiki, which is just a collection of .md files in a directory structure. The wiki includes summaries of all the data in raw/, backlinks, and then it categorizes data into concepts, writes articles for them, and links them all. To convert web articles into .md files I like to use the Obsidian Web Clipper extension, and then I also use a hotkey to download all the related images to local so that my LLM can easily reference them.  
数据导入：

我会将源文档（文章、论文、仓库、数据集、图片等）索引到一个原始目录中，然后用大型语言模型（LLM）逐步“编译”一个 wiki，wiki 其实就是目录结构中的.md 文件集合。维基包含所有数据的原始摘要、反向链接，然后将数据分类为概念，撰写相关文章并链接所有内容。要把网页文章转换成.md 文件，我喜欢用 Obsidian Web Clipper 扩展，然后用快捷键把所有相关图片下载到本地，这样我的 LLM 就能轻松引用。  
  
IDE:

I use Obsidian as the IDE "frontend" where I can view the raw data, the the compiled wiki, and the derived visualizations. Important to note that the LLM writes and maintains all of the data of the wiki, I rarely touch it directly. I've played with a few Obsidian plugins to render and view data in other ways (e.g. Marp for slides).  
IDE：

我用 Obsidian 作为 IDE 的“前端”，可以查看原始数据、编译后的维基和衍生的可视化。需要注意的是，LLM 负责编写和维护维基的所有数据，我很少直接接触它。我也尝试过几个 Obsidian 插件来渲染和查看数据（比如幻灯片用的 Marp）。  
  
Q&A:

Where things get interesting is that once your wiki is big enough (e.g. mine on some recent research is ~100 articles and ~400K words), you can ask your LLM agent all kinds of complex questions against the wiki, and it will go off, research the answers, etc. I thought I had to reach for fancy RAG, but the LLM has been pretty good about auto-maintaining index files and brief summaries of all the documents and it reads all the important related data fairly easily at this ~small scale.  
问答：

有趣的是，一旦你的维基足够大（比如我最近的研究有~100 篇文章和~40 万字），你可以在维基上向你的 LLM 代理提出各种复杂的问题，维基会自动启动，查找答案等等。我以为我得用高级的 RAG，但 LLM 在自动维护索引文件和所有文档的简要摘要方面做得相当不错，而且在这~小规模范围内，它能相当轻松地读取所有重要相关数据。  
  
Output:

Instead of getting answers in text/terminal, I like to have it render markdown files for me, or slide shows (Marp format), or matplotlib images, all of which I then view again in Obsidian. You can imagine many other visual output formats depending on the query. Often, I end up "filing" the outputs back into the wiki to enhance it for further queries. So my own explorations and queries always "add up" in the knowledge base.  
输出：

我不喜欢让它帮我渲染 markdown 文件，或者做幻灯片（Marp 格式），或者 matplotlib 图片，然后再用 Obsidian 查看。你可以根据查询类型想象许多其他的视觉输出格式。我经常会把输出“归档”回维基，以便进一步查询。所以我自己的探索和查询总是会“累积”在知识库中。  
  
Linting:

I've run some LLM "health checks" over the wiki to e.g. find inconsistent data, impute missing data (with web searchers), find interesting connections for new article candidates, etc., to incrementally clean up the wiki and enhance its overall data integrity. The LLMs are quite good at suggesting further questions to ask and look into.  
绒毛：

我对维基做过一些大型语言模型的“健康检查”，比如发现不一致的数据、用网页搜索者补值缺失的数据、寻找新条目候选的有趣联系等，逐步清理维基，提升整体数据完整性。LLMs 很擅长建议进一步的问题和研究。  
  
Extra tools:

I find myself developing additional tools to process the data, e.g. I vibe coded a small and naive search engine over the wiki, which I both use directly (in a web ui), but more often I want to hand it off to an LLM via CLI as a tool for larger queries.  
额外工具：

我发现自己在开发额外的工具来处理数据，比如我用一个小巧且朴素的搜索引擎覆盖维基，我直接在网页界面中使用，但更多时候我想通过 CLI 交给大型语言模型，作为处理大型查询的工具。  
  
Further explorations:

As the repo grows, the natural desire is to also think about synthetic data generation + finetuning to have your LLM "know" the data in its weights instead of just context windows.  
进一步探讨：

随着仓库的增长，自然会考虑合成数据生成+微调，让你的 LLM“知道”数据的权重，而不仅仅是上下文窗口。  
  
TLDR: raw data from a given number of sources is collected, then compiled by an LLM into a .md wiki, then operated on by various CLIs by the LLM to do Q&A and to incrementally enhance the wiki, and all of it viewable in Obsidian. You rarely ever write or edit the wiki manually, it's the domain of the LLM. I think there is room here for an incredible new product instead of a hacky collection of scripts.  
总结：从一定数量的来源收集原始数据，然后由大型语言模型汇编成.md 维基，再由 LLM 的各种 CLI 操作以进行问答和逐步增强维基，所有数据都能在 Obsidian 中查看。你很少会手动编写或编辑维基，那是大型语言模型的领域。我认为这里有空间推出一款令人难以置信的新产品，而不是一堆草率的脚本集合。

Oh and in the natural extrapolation, you could imagine that every question to a frontier grade LLM spawns a team of LLMs to automate the whole thing: iteratively construct an entire ephemeral wiki, lint it, loop a few times, then write a full report. Way beyond a `.decode()`.  
哦，顺便说一句，你可以想象，每一个向前沿级 LLM 提问的问题，都会引发一支团队来自动化整个过程：反复构建一个完整的临时维基，进行 linping，循环几次，然后写一份完整的报告。远远超过了“.decode（）”。