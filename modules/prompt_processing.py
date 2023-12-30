import random
from modules.settings import styles, default_style, allstyles


def process_prompt(style, prompt):
    prompt, negative_prompt = get_negative_prompt(prompt)
    if style:
        prompt, negative_prompt = apply_style(style, prompt, negative_prompt)
    return prompt, negative_prompt


def apply_style(style, prompt, negative_prompt):
    output_prompt = []
    output_negative_prompt = []

    while "Style: Pick Random" in style:
        style[style.index("Style: Pick Random")] = random.choice(allstyles)

    if not style:
        return prompt, negative_prompt

    for s in style:
        p, n = styles.get(s, default_style)
        output_prompt.append(p)
        output_negative_prompt.append(n)

    output_prompt = ", ".join(output_prompt)
    output_negative_prompt = ", ".join(output_negative_prompt)

    output_prompt = output_prompt.replace("{prompt}", prompt)
    output_negative_prompt += ", " + negative_prompt

    return output_prompt, output_negative_prompt


def get_negative_prompt(prompt):
    positive_prompt, negative_prompt = prompt.split("--no ")
    return positive_prompt.strip(), negative_prompt.strip()
