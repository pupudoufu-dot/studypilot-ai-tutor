"use strict";

const samples = {
  concept: {
    question: "解方程 2x + 3 = 11",
    answer: "x = 7",
    reasoning: "我把移项理解成两边都加 3，等式的概念有点混淆。",
  },
  misread: {
    question: "某商品打八折后为 160 元，求原价。",
    answer: "128 元",
    reasoning: "我看错了，把八折后价格当成了原价再乘 0.8。",
  },
  calculation: {
    question: "计算 3/4 + 1/6",
    answer: "4/10",
    reasoning: "我知道要通分，但是通分错了，中间数字算错。",
  },
  method: {
    question: "已知直角三角形两直角边，求斜边。",
    answer: "两边直接相加",
    reasoning: "我公式选错了，不知道应该用什么方法，所以选了边长相加。",
  },
  unclear: {
    question: "求函数在给定区间上的最大值。",
    answer: "最大值是 4",
    reasoning: "我做完后觉得结果不太对。",
  },
};

const labels = {
  concept_gap: "概念理解偏差",
  misread_question: "审题信息偏差",
  calculation_error: "计算执行失误",
  method_selection: "方法选择错误",
  procedure_gap: "中间步骤缺失",
  needs_clarification: "证据不足，需补充信息",
};

const keywordRules = {
  concept_gap: ["概念不懂", "不理解定义", "以为", "没弄清", "混淆", "理解成", "不知道含义", "定义记反", "条件理解错", "概念"],
  misread_question: ["看错", "漏看", "读成", "忽略", "没注意", "审题", "少看", "当成", "题意理解偏了"],
  calculation_error: ["算错", "计算错", "抄错", "符号写反", "进位", "约分错", "通分错", "运算失误", "数字带错"],
  method_selection: ["方法不对", "不知道用什么", "公式选错", "选了", "不该用", "用了错误", "思路方向", "方法选错", "公式套错"],
  procedure_gap: ["不知道下一步", "步骤忘了", "卡在", "做到这里", "接下来", "顺序", "漏了一步", "中间步骤", "不会继续"],
};

const hints = {
  concept_gap: [
    "先回想这道题涉及的核心定义，它成立需要哪些条件？",
    "把题目中的已知条件逐一对应到定义，再检查是否遗漏限制。",
    "请写出定义并代入本题条件，然后重新尝试完整求解。",
  ],
  misread_question: [
    "先别计算，重新圈出题目要求和所有限定词。",
    "对照你的答案，检查单位、范围、正负号或‘至少/至多’等词。",
    "请用自己的话复述题意，再根据复述后的目标重新作答。",
  ],
  calculation_error: [
    "思路可能是对的，先逐行检查数字和运算符。",
    "把中间结果单独重算一次，重点检查符号、进位、通分或约分。",
    "保留原方法，但从第一步开始重新计算并核对每个中间值。",
  ],
  method_selection: [
    "先判断题目给出的信息适合哪一类方法，不要急着套公式。",
    "比较两种可能的方法：各自需要什么条件？本题满足哪一种？",
    "请先写出选择该方法的理由，再用满足条件的方法重新求解。",
  ],
  procedure_gap: [
    "回顾当前结果：它距离题目目标还差什么信息？",
    "把完整解题流程列成三步，定位你现在处于哪一步。",
    "从当前中间结果出发，补上下一步变换，再继续完成剩余步骤。",
  ],
};

const transfers = {
  concept_gap: "换一组数值，但保持同一概念条件；先说明定义，再完成作答。",
  misread_question: "完成一道包含不同限定词的同类题，并先用自己的话复述题意。",
  calculation_error: "完成一道步骤相同但数字不同的题，并保留全部中间计算。",
  method_selection: "比较两道外观相似但解法不同的题，说明方法选择依据。",
  procedure_gap: "完成一道同流程变式题，并为每一步标注目的。",
};

const questionInput = document.querySelector("#question");
const answerInput = document.querySelector("#answer");
const reasoningInput = document.querySelector("#reasoning");
const form = document.querySelector("#diagnosis-form");
const emptyState = document.querySelector("#empty-state");
const resultContent = document.querySelector("#result-content");
const resultStatus = document.querySelector("#result-status");
const diagnosisLabel = document.querySelector("#diagnosis-label");
const evidenceList = document.querySelector("#evidence-list");
const confidenceValue = document.querySelector("#confidence-value");
const confidenceBar = document.querySelector("#confidence-bar");
const routeLabel = document.querySelector("#route-label");
const actionKind = document.querySelector("#action-kind");
const actionMessage = document.querySelector("#action-message");
const budgetLabel = document.querySelector("#budget-label");
const retryButton = document.querySelector("#retry-button");
const successButton = document.querySelector("#success-button");

let session = { diagnosis: null, hintIndex: 0, budget: 3 };

function loadSample(name) {
  const sample = samples[name];
  questionInput.value = sample.question;
  answerInput.value = sample.answer;
  reasoningInput.value = sample.reasoning;
  document.querySelectorAll(".sample-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.sample === name);
  });
}

function diagnose(reasoning) {
  const matches = Object.entries(keywordRules)
    .map(([type, words]) => ({ type, evidence: words.filter((word) => reasoning.includes(word)) }))
    .filter((item) => item.evidence.length > 0)
    .sort((a, b) => b.evidence.length - a.evidence.length);

  if (!matches.length) {
    return { type: "needs_clarification", confidence: 0.35, evidence: [] };
  }

  const tied = matches.length > 1 && matches[0].evidence.length === matches[1].evidence.length;
  if (tied) {
    return { type: "needs_clarification", confidence: 0.58, evidence: matches[0].evidence };
  }

  return {
    type: matches[0].type,
    confidence: Math.min(0.72 + 0.08 * (matches[0].evidence.length - 1), 0.94),
    evidence: matches[0].evidence,
  };
}

function setTimeline(activeStep) {
  const order = ["diagnosis", "tutor", "planner"];
  const activeIndex = order.indexOf(activeStep);
  document.querySelectorAll(".timeline-step").forEach((step, index) => {
    step.classList.toggle("active", index === activeIndex);
    step.classList.toggle("done", index < activeIndex || (activeStep === "diagnosis" && index === 0));
  });
}

function displayResult(result) {
  emptyState.classList.add("hidden");
  resultContent.classList.remove("hidden");
  resultStatus.textContent = "诊断完成";
  resultStatus.classList.add("ready");
  diagnosisLabel.textContent = labels[result.type];
  confidenceValue.textContent = `${Math.round(result.confidence * 100)}%`;
  confidenceBar.style.width = `${result.confidence * 100}%`;
  evidenceList.innerHTML = result.evidence.length
    ? result.evidence.map((word) => `<span>${escapeHtml(word)}</span>`).join("")
    : "<span class=\"muted-chip\">未找到可靠证据</span>";

  if (result.type === "needs_clarification") {
    routeLabel.textContent = "CLARIFY";
    actionKind.textContent = "补充追问";
    actionMessage.textContent = "你能说说从哪一步开始不确定，或者当时为什么选择这个方法吗？";
    budgetLabel.textContent = "暂不消耗提示预算";
    retryButton.classList.add("hidden");
    successButton.classList.add("hidden");
    setTimeline("diagnosis");
    return;
  }

  showHint();
}

function showHint() {
  routeLabel.textContent = "TUTOR";
  actionKind.textContent = `分级提示 · Level ${session.hintIndex + 1}`;
  actionMessage.textContent = hints[session.diagnosis.type][session.hintIndex];
  budgetLabel.textContent = `Hint Budget · ${session.budget}`;
  retryButton.classList.remove("hidden");
  successButton.classList.remove("hidden");
  setTimeline("tutor");
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  })[character]);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  session = { diagnosis: diagnose(reasoningInput.value.trim()), hintIndex: 0, budget: 2 };
  displayResult(session.diagnosis);
});

retryButton.addEventListener("click", () => {
  if (session.budget <= 0) {
    routeLabel.textContent = "ESCALATE";
    actionKind.textContent = "Fallback · 提示预算已用完";
    actionMessage.textContent = "停止重复提示：建议回到核心定义，或请求教师进一步帮助。";
    budgetLabel.textContent = "Hint Budget · 0";
    retryButton.classList.add("hidden");
    setTimeline("tutor");
    return;
  }
  session.budget -= 1;
  session.hintIndex = Math.min(session.hintIndex + 1, 2);
  showHint();
});

successButton.addEventListener("click", () => {
  routeLabel.textContent = "TRANSFER";
  actionKind.textContent = "迁移验证";
  actionMessage.textContent = `【同知识点 · 变式练习】${transfers[session.diagnosis.type]}`;
  budgetLabel.textContent = "Planner 已生成任务";
  retryButton.classList.add("hidden");
  successButton.classList.add("hidden");
  setTimeline("planner");
});

document.querySelectorAll(".sample-chip").forEach((button) => {
  button.addEventListener("click", () => loadSample(button.dataset.sample));
});

loadSample("concept");
