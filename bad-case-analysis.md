# Bad Case Analysis

## 1. No evidence in the learner's reasoning

**Input:** “I just felt this should be the answer.”

**Baseline behavior:** forces a `concept_gap` label.

**StudyPilot behavior:** returns `needs_clarification` with low confidence and
asks where the learner first became uncertain.

**Product decision:** uncertainty should change the route, not only appear as a
number next to a hard decision.

## 2. Method and procedure signals appear together

**Input:** “I chose substitution, then got stuck after the first step.”

**Risk:** the learner may have selected the wrong method, or may understand the
method but lack the next procedural step.

**Current handling:** tied evidence produces a lower confidence score and routes
to clarification.

**Next iteration:** ask a contrastive question: “Why did you choose
substitution, and what result did you expect after the first step?”

## 3. Correct label does not guarantee a useful hint

**Input:** A calculation mistake is diagnosed correctly, but the hint “check
your arithmetic” may still be too generic.

**Current handling:** three levels gradually narrow the location of the error.

**Next iteration:** use structured intermediate steps from the learner's work
to point to a specific line without revealing the final answer.

## 4. Synthetic language is cleaner than real learner language

**Risk:** real inputs may be shorter, colloquial, incomplete, or contain several
causes at once.

**Mitigation:** treat the public benchmark as a policy regression suite, not a
generalization benchmark. Real-user validation is future work and must be
reported separately.

