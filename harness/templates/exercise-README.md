# Exercise — {{title}}

Week {{week}} · Day {{day}} · `{{id}}` · ~60–90 min
Notes: [weeks/{{rel}}.html](https://2494-gen-ai-cn.github.io/training/weeks/{{rel}}.html) · Demos: [2494-Gen-AI-CN/demos](https://github.com/2494-Gen-AI-CN/demos)

## Task

<One paragraph: what to build and why it matters for today's topic.>

## Acceptance criteria

- [ ] ...
- [ ] ...
- [ ] All tests pass: `python -m pytest -q`

## Getting started

Run these from your clone of the training repo. They copy this exercise into your own repository (`<FirstnameLastname>`, the one you created in the Week 1 Git exercise) at the same path, and you work in that copy. The paths assume the two repositories sit side by side; adjust `..` if yours do not.

```
git pull
mkdir -p ../<FirstnameLastname>/{{rel}}
cp -r exercises/{{rel}}/* ../<FirstnameLastname>/{{rel}}/
cd ../<FirstnameLastname>/{{rel}}
python -m pytest -q          # everything fails until you implement starter/<module>.py
```

Implement the functions in `starter/<module>.py` (each has a docstring and currently raises `NotImplementedError`). Run the tests as you go.

**Hand-in:** commit as you go and push to `main` of your `<FirstnameLastname>` repository; the trainer reads `{{rel}}/` there.

## Hints

- ...
