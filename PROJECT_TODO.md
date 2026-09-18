# Project TODOs

## Product Overview
- [x] Confirm Live Share visibility and write access
- [ ] Finalize product brief and core success criteria
- [ ] Define MVP scope vs. future expansion
- [ ] Choose app stack and repo structure

## User Tracks and Quiz Flow
- [ ] Design branching flow for first-time freshman vs. transfer student
- [ ] Define freshman quiz dimension set and scoring model
- [ ] Define transfer quiz dimension set, pain-point checklist, and scoring model
- [ ] Map question logic to weighted categories (academic/career, social/lifestyle, environment, practical)
- [ ] Establish question wording and answer formats for each track

## Freshman Track
- [ ] Implement freshman questions for academic/career preferences
- [ ] Implement freshman questions for social/lifestyle preferences
- [ ] Implement freshman questions for environment and practical factors
- [ ] Add weights for intended major, class size, research vs. teaching, grad school vs. jobs
- [ ] Add weights for party culture, Greek life, athletics, diversity, setting, dorm culture
- [ ] Add weights for weather, campus size, distance from home, budget, selectivity comfort zone, student-to-faculty ratio

## Transfer Track
- [ ] Implement transfer-specific questions (school type, credits completed, timeline, goals)
- [ ] Build pain-point checklist for what user disliked about prior school
- [ ] Define scoring adjustments for pain-point match penalties
- [ ] Add logic to actively subtract points from schools with similar disliked traits
- [ ] Add optional free-text reasoning field and classification strategy
- [ ] Design transfer support logic for advising quality, articulation, and credit transfer needs

## Matching Algorithm
- [ ] Define scoring formula: positive preference weights minus penalties from disliked traits
- [ ] Build category-based weighting rules
- [ ] Add post-quiz user controls to adjust dimension importance and rerank results
- [ ] Decide how to combine categorical preferences with school metadata
- [ ] Return top 5 matches with percentage match scores instead of a single winner

## Results Page
- [ ] Build top-5 ranked results view
- [ ] Add “explain the match” rationale for each school
- [ ] Show transfer-specific pain-point explanation
- [ ] Add comparison tool for 2–3 schools side by side
- [ ] Add shareable result card / viral quiz style presentation
- [ ] Add retake flow with adjusted weights

## Transfer-Specific Features
- [ ] Research credit transfer estimator model and rough transfer % logic
- [ ] Add articulation agreement lookup support for community college pipelines
- [ ] Add transfer-friendly badge/filter for schools with strong support systems
- [ ] Estimate time-to-degree impact for transfer students
- [ ] Show major- and sequence-specific transfer considerations

## General Features
- [ ] Add real student review snippets per school
- [ ] Add cost estimator tied to residency and aid situation
- [ ] Add “Schools like this one” recommendations for the top result
- [ ] Add filter and sorting options for school characteristics

## Data and AI Considerations
- [ ] Decide whether to use rules-based or LLM classification for free-text pain points
- [ ] Define school dataset schema and metadata fields required
- [ ] Source or estimate transfer credit data
- [ ] Validate school attributes for campus culture, setting, selectivity, party scene, diversity, and transfer support

## Open Questions / Next Steps
- [ ] Source or estimate credit-transfer data (trickiest data problem)
- [ ] Decide on LLM vs. rules-based classification for free-text pain points
- [ ] Design the branching flow diagram for freshman vs. transfer split
- [ ] Define full scoring and weighting algorithm
- [ ] Confirm whether the app should be a web app, mobile app, or both
- [ ] Decide if this is a startup MVP or a prototype/demo product

## Notes
- Matching logic should avoid schools shaped like the user’s previous one, not just seek positive preferences.
- Transfer pain points should be displayed as selectable checklist items for clean scoring.
- Results should be explainable and re-sortable after users adjust weight emphasis.
- This file is intended to be shared with Live Share participants and revised as the product direction gets locked in.


