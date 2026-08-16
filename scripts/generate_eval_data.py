"""Generate the public 200-case synthetic benchmark deterministically."""

from __future__ import annotations

import json
from pathlib import Path


KNOWLEDGE_POINTS = [
    "整数四则运算", "小数乘法", "小数除法", "分数加法", "分数减法",
    "分数乘法", "分数除法", "百分数", "比例", "比的化简",
    "一元一次方程", "二元一次方程组", "不等式", "绝对值", "因式分解",
    "整式乘法", "平方差公式", "完全平方公式", "二次函数", "一次函数",
    "反比例函数", "勾股定理", "相似三角形", "全等三角形", "圆周角",
    "平行线", "角平分线", "概率初步", "平均数", "中位数",
    "方差", "排列组合", "数列", "指数运算", "根式运算",
    "集合", "充分必要条件", "三角函数", "向量", "立体几何",
]


ERROR_VARIANTS: dict[str, list[str]] = {
    "concept_gap": [
        "我以为{kp}里的两个量可以直接互换。",
        "这个概念不懂，所以我照着之前的题写了。",
        "我不理解定义，不知道限制条件为什么要满足。",
        "我以为定义只看结果，不需要检查过程。",
        "我不理解定义里这个条件的作用。",
        "我没弄清{kp}和相邻概念的区别。",
        "我把{kp}与另一个概念混淆了。",
        "我把这里理解成只需要满足一个条件。",
        "我把定义记反了，所以判断方向相反。",
        "我只是凭感觉选的，说不清原因。",
    ],
    "misread_question": [
        "我看错了题目要求，把求差看成了求和。",
        "我漏看了最后一个限定条件。",
        "我把‘至少’读成了‘至多’。",
        "我看错了单位，所以直接代入了。",
        "我漏看了括号外面的负号。",
        "我忽略了题目给出的取值范围。",
        "我没注意题目问的是不正确的一项。",
        "审题时少看了一行已知条件。",
        "我把已知条件当成了最终要求。",
        "我按印象做的，没有重新读题。",
    ],
    "calculation_error": [
        "方法会做，但我算错了最后一步。",
        "这里计算错了，把7乘8写成了54。",
        "我抄错了上一行的数字。",
        "中间一步算错了，后面的结果都受影响。",
        "我把加号抄错成减号。",
        "移项时符号写反了。",
        "竖式进位时少加了1。",
        "分数约分错了，分子分母没有同除。",
        "这里通分错了，公分母选得不一致。",
        "步骤看起来都对，但答案就是不一样。",
    ],
    "method_selection": [
        "我用了这个方法，但好像方法不对。",
        "我不知道用什么方法，所以随便选了一个。",
        "我把公式选错了，套成另一种情况。",
        "做到一半发现方法不对，只能重新开始。",
        "我不知道用什么公式，先用了最熟悉的。",
        "这里不该用代入法，我却一直代入。",
        "我用了错误的公式条件。",
        "我的思路方向一开始就偏了。",
        "本来应该分类讨论，却用了统一计算。",
        "我知道几个公式，但不知道这题该选哪个。",
    ],
    "procedure_gap": [
        "我做到这里后不知道下一步。",
        "步骤忘了，只记得第一步。",
        "我卡在化简之后，不会继续。",
        "前两步会做，但不知道下一步怎么变形。",
        "步骤忘了，不确定先移项还是先合并。",
        "我做到这里就停住了。",
        "接下来该做什么我想不起来。",
        "我把解题顺序弄乱了。",
        "中间漏了一步，所以连接不上。",
        "我能跟着例题做，换一道就接不上。",
    ],
}


def build_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    error_types = list(ERROR_VARIANTS)
    for kp_index, knowledge_point in enumerate(KNOWLEDGE_POINTS):
        for type_index, error_type in enumerate(error_types):
            variant_index = (kp_index + type_index * 3) % 10
            reasoning = ERROR_VARIANTS[error_type][variant_index].format(kp=knowledge_point)
            cases.append(
                {
                    "case_id": f"case-{len(cases) + 1:03d}",
                    "knowledge_point": knowledge_point,
                    "question": f"完成一道关于{knowledge_point}的练习，并写出关键步骤。",
                    "student_answer": "示例错误答案",
                    "student_reasoning": reasoning,
                    "expected_error_type": error_type,
                    "correct_answer": "标准答案仅用于评测答案暴露，不用于诊断分类。",
                    "source": "synthetic",
                }
            )
    return cases + build_challenge_cases()


def build_challenge_cases() -> list[dict[str, object]]:
    """Return plausible cases that are intentionally independent of templates."""
    scenarios = [
        ("challenge-001", "\u4e00\u5143\u4e00\u6b21\u65b9\u7a0b", "\u6211\u4e0d\u662f\u770b\u9519\u9898\uff0c\u662f\u628a\u79fb\u9879\u7684\u7b26\u53f7\u5199\u53cd\u4e86\u3002", "calculation_error"),
        ("challenge-002", "\u5206\u6570\u52a0\u6cd5", "\u6211\u4e0d\u662f\u516c\u5f0f\u9009\u9519\uff0c\u901a\u5206\u65f6\u5206\u6bcd\u7b97\u9519\u4e86\u3002", "calculation_error"),
        ("challenge-003", "\u4e8c\u6b21\u51fd\u6570", "\u6211\u4e0d\u662f\u8ba1\u7b97\u9519\uff0c\u800c\u662f\u516c\u5f0f\u9009\u9519\u4e86\u3002", "method_selection"),
        ("challenge-004", "\u4e0d\u7b49\u5f0f", "\u6211\u6309\u5370\u8c61\u505a\uff0c\u6ca1\u91cd\u65b0\u8bfb\u9898\uff0c\u628a\u81f3\u5c11\u5f53\u6210\u81f3\u591a\u3002", "misread_question"),
        ("challenge-005", "\u5145\u5206\u5fc5\u8981\u6761\u4ef6", "\u6211\u4e0d\u662f\u6f0f\u770b\u6761\u4ef6\uff0c\u800c\u662f\u4e0d\u7406\u89e3\u5b9a\u4e49\u91cc\u7684\u9650\u5236\u6761\u4ef6\u3002", "concept_gap"),
        ("challenge-006", "\u56e0\u5f0f\u5206\u89e3", "\u6211\u4e0d\u662f\u516c\u5f0f\u9009\u9519\uff0c\u662f\u5316\u7b80\u540e\u4e0d\u77e5\u9053\u4e0b\u4e00\u6b65\u600e\u4e48\u505a\u3002", "procedure_gap"),
        ("challenge-007", "\u6bd4\u4f8b", "\u6211\u89c9\u5f97\u7b54\u6848\u4e0d\u5bf9\uff0c\u4f46\u8bf4\u4e0d\u51fa\u54ea\u4e00\u6b65\u6709\u95ee\u9898\u3002", "needs_clarification"),
        ("challenge-008", "\u5c0f\u6570\u9664\u6cd5", "\u6211\u53ef\u80fd\u770b\u9519\u9898\uff0c\u4e5f\u53ef\u80fd\u7b97\u9519\u4e86\u3002", "needs_clarification"),
        ("challenge-009", "\u5e73\u5747\u6570", "\u65b9\u6cd5\u548c\u8ba1\u7b97\u597d\u50cf\u90fd\u6709\u95ee\u9898\uff0c\u4f46\u6211\u8bb0\u4e0d\u6e05\u4e86\u3002", "needs_clarification"),
        ("challenge-010", "\u4e09\u89d2\u51fd\u6570", "\u8001\u5e08\u8bf4\u6211\u9519\u4e86\uff0c\u4f46\u6211\u4e0d\u77e5\u9053\u539f\u56e0\u3002", "needs_clarification"),
    ]
    return [
        {
            "case_id": case_id,
            "knowledge_point": knowledge_point,
            "question": f"\u5b8c\u6210\u4e00\u9053\u5173\u4e8e{knowledge_point}\u7684\u7ec3\u4e60\uff0c\u5e76\u5199\u51fa\u5173\u952e\u6b65\u9aa4\u3002",
            "student_answer": "\u793a\u4f8b\u9519\u8bef\u7b54\u6848",
            "student_reasoning": reasoning,
            "expected_error_type": expected_error_type,
            "correct_answer": "\u6807\u51c6\u7b54\u6848\u4ec5\u7528\u4e8e\u8bc4\u6d4b\u7b54\u6848\u66b4\u9732\uff0c\u4e0d\u7528\u4e8e\u8bca\u65ad\u5206\u7c7b\u3002",
            "source": "challenge_synthetic",
        }
        for case_id, knowledge_point, reasoning, expected_error_type in scenarios
    ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "evals" / "cases.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for case in build_cases():
            handle.write(json.dumps(case, ensure_ascii=False) + "\n")
    print(f"Wrote {len(build_cases())} cases to {output}")


if __name__ == "__main__":
    main()

