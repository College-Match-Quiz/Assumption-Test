const app = document.getElementById('app');
const retakeBtn = document.getElementById('retakeBtn');

const freshmanQuestions = [
  {
    id: 'major',
    title: 'What do you want to study?',
    type: 'single',
    description: 'Choose the closest fit for your interests.',
    options: [
      { value: 'engineering', label: 'Engineering / STEM', note: 'Strong technical programs and research' },
      { value: 'business', label: 'Business', note: 'Career-driven and internship-focused' },
      { value: 'liberal_arts', label: 'Liberal arts / social sciences', note: 'Broad academics and discussion-heavy classes' },
      { value: 'undecided', label: 'Undecided / exploring', note: 'I want flexibility and broad options' },
      { value: 'health', label: 'Health / pre-med / nursing', note: 'Competitive pathways and clinical exposure' }
    ]
  },
  {
    id: 'classSize',
    title: 'How important is small class size?',
    type: 'single',
    options: [
      { value: 'small', label: 'Very important', note: 'I prefer seminars and close faculty access' },
      { value: 'balanced', label: 'Somewhat important', note: 'Hybrid lecture + discussion model is fine' },
      { value: 'large', label: 'Not a big deal', note: 'I’m comfortable in big lectures' }
    ]
  },
  {
    id: 'campusSize',
    title: 'What type of campus feels right?',
    type: 'single',
    options: [
      { value: 'small', label: 'Compact / walkable', note: 'I want a close-knit campus' },
      { value: 'medium', label: 'Medium-sized', note: 'A balance of convenience and energy' },
      { value: 'large', label: 'Large / bustling', note: 'Big university energy is good' }
    ]
  },
  {
    id: 'setting',
    title: 'What setting do you prefer?',
    type: 'single',
    options: [
      { value: 'urban', label: 'Urban', note: 'City life, internships, transit' },
      { value: 'suburban', label: 'Suburban', note: 'Balance of campus and nearby amenities' },
      { value: 'rural', label: 'Rural', note: 'Nature, quieter environment, less city buzz' }
    ]
  },
  {
    id: 'partyCulture',
    title: 'How much do you care about party culture?',
    type: 'single',
    options: [
      { value: 'low', label: 'Not important', note: 'I’d rather focus on academics and clubs' },
      { value: 'medium', label: 'Somewhat', note: 'A lively scene is nice but not central' },
      { value: 'high', label: 'Important', note: 'I want big social energy and weekends' }
    ]
  },
  {
    id: 'sports',
    title: 'How important is athletics and school spirit?',
    type: 'single',
    options: [
      { value: 'low', label: 'Not important', note: 'I’m not chasing game-day culture' },
      { value: 'medium', label: 'Somewhat', note: 'I enjoy spirit, but it’s not everything' },
      { value: 'high', label: 'Very important', note: 'Big game-day culture matters to me' }
    ]
  },
  {
    id: 'diversity',
    title: 'How important is campus diversity and climate?',
    type: 'single',
    options: [
      { value: 'important', label: 'Very important', note: 'I want a strong sense of inclusion and variety' },
      { value: 'moderate', label: 'Somewhat important', note: 'It matters, but not the top driver' },
      { value: 'not', label: 'Not a major driver', note: 'I’m mostly looking at academics and fit' }
    ]
  },
  {
    id: 'budget',
    title: 'What matters most for cost?',
    type: 'single',
    options: [
      { value: 'instate', label: 'In-state value is essential', note: 'Affordable public options are a priority' },
      { value: 'aid', label: 'Need strong financial aid', note: 'Cost needs to be manageable overall' },
      { value: 'flexible', label: 'I can be flexible on cost', note: 'I’m open to pricier schools if fit is better' }
    ]
  },
  {
    id: 'weather',
    title: 'Weather preference?',
    type: 'single',
    options: [
      { value: 'mild', label: 'Mild / warm', note: 'I prefer sunshine and less winter' },
      { value: 'balanced', label: 'Balanced', note: 'I’m fine with seasons, not picky' },
      { value: 'cold', label: 'Cold / snow', note: 'I like winter and snow opportunities' }
    ]
  },
  {
    id: 'homeDistance',
    title: 'How far from home do you want to be?',
    type: 'single',
    options: [
      { value: 'close', label: 'Close to home', note: 'I want to stay nearby' },
      { value: 'moderate', label: 'A moderate distance', note: 'I want some independence but not too far' },
      { value: 'far', label: 'Far away', note: 'I want the full new-environment experience' }
    ]
  }
];

const transferQuestions = [
  {
    id: 'schoolType',
    title: 'What type of school are you coming from?',
    type: 'single',
    options: [
      { value: 'community_college', label: 'Community college', note: 'I’m planning to transfer after earning credits' },
      { value: 'four_year', label: '4-year college', note: 'I’m transferring from another university' },
      { value: 'none', label: 'No college yet', note: 'I’m a transfer-ish student but not from a prior college' }
    ]
  },
  {
    id: 'transferReason',
    title: 'What is your main reason for transferring?',
    type: 'single',
    options: [
      { value: 'cost', label: 'Cost / affordability', note: 'I want lower tuition or better aid' },
      { value: 'major', label: 'Better major/program fit', note: 'My current school doesn’t offer the right academic path' },
      { value: 'better_fit', label: 'Better overall fit', note: 'I want a better campus culture and environment' },
      { value: 'home', label: 'Closer to home', note: 'I want to be nearer family or support network' },
      { value: 'reset', label: 'Academic reset', note: 'I need a fresh start' }
    ]
  },
  {
    id: 'painPoints',
    title: 'What didn’t you like about your old school?',
    type: 'multi',
    options: [
      { value: 'too_big', label: 'Too big / felt anonymous' },
      { value: 'too_small', label: 'Too small / everyone knew my business' },
      { value: 'no_party', label: 'No party scene / dead weekends' },
      { value: 'party_too_much', label: 'Party culture was too intense' },
      { value: 'too_far', label: 'Too far from home / isolated' },
      { value: 'too_close', label: 'Too close to home / no distance' },
      { value: 'weak_major', label: 'Weak program in my major' },
      { value: 'too_expensive', label: 'Too expensive / bad aid' },
      { value: 'cliquey', label: 'Felt cliquey / not diverse enough' },
      { value: 'bad_advising', label: 'Bad advising / credit issues' },
      { value: 'wrong_location', label: 'Wrong location vibe (too rural/urban)' }
    ]
  },
  {
    id: 'timeline',
    title: 'When do you want to transfer?',
    type: 'single',
    options: [
      { value: 'fall', label: 'Fall transfer', note: 'Next academic year' },
      { value: 'spring', label: 'Spring transfer', note: 'Semester transfer' },
      { value: 'flexible', label: 'Flexible / no rush', note: 'I can be flexible' }
    ]
  },
  {
    id: 'transferPriority',
    title: 'Which factor matters most in the next school?',
    type: 'single',
    options: [
      { value: 'credit_transfer', label: 'Credit transfer ease', note: 'I need my classes to count' },
      { value: 'fit', label: 'Campus vibe and fit', note: 'I want a better social and academic match' },
      { value: 'cost', label: 'Affordability', note: 'I need the best value' },
      { value: 'location', label: 'Location / distance', note: 'Proximity and setting are important' }
    ]
  }
];

const colleges = [
  {
    name: 'University of Michigan',
    type: 'public',
    setting: 'urban',
    campusSize: 'large',
    party: 'high',
    sports: 'high',
    diversity: 'high',
    classSize: 'large',
    research: 'high',
    business: 8,
    engineering: 9,
    liberal_arts: 8,
    health: 7,
    undecided: 8,
    cost: 6,
    weather: 'cold',
    homeDistance: 'far',
    transferFriendly: 7,
    description: 'Big-school energy, strong academics, high school spirit, and a very active campus life.'
  },
  {
    name: 'University of Texas at Austin',
    type: 'public',
    setting: 'urban',
    campusSize: 'large',
    party: 'high',
    sports: 'high',
    diversity: 'high',
    classSize: 'large',
    research: 'high',
    business: 9,
    engineering: 9,
    liberal_arts: 8,
    health: 7,
    undecided: 8,
    cost: 7,
    weather: 'mild',
    homeDistance: 'far',
    transferFriendly: 7,
    description: 'Strong career preparation, vibrant social life, and big-university scale.'
  },
  {
    name: 'University of North Carolina at Chapel Hill',
    type: 'public',
    setting: 'suburban',
    campusSize: 'medium',
    party: 'medium',
    sports: 'high',
    diversity: 'high',
    classSize: 'medium',
    research: 'high',
    business: 7,
    engineering: 6,
    liberal_arts: 9,
    health: 8,
    undecided: 8,
    cost: 6,
    weather: 'balanced',
    homeDistance: 'moderate',
    transferFriendly: 6,
    description: 'A classic public flagship with strong academics, school spirit, and a compelling campus culture.'
  },
  {
    name: 'Georgia Tech',
    type: 'public',
    setting: 'urban',
    campusSize: 'medium',
    party: 'medium',
    sports: 'medium',
    diversity: 'high',
    classSize: 'small',
    research: 'high',
    business: 6,
    engineering: 10,
    liberal_arts: 4,
    health: 4,
    undecided: 6,
    cost: 6,
    weather: 'mild',
    homeDistance: 'moderate',
    transferFriendly: 7,
    description: 'Tech-first, academically intense, and strong on research and career outcomes.'
  },
  {
    name: 'University of Florida',
    type: 'public',
    setting: 'suburban',
    campusSize: 'large',
    party: 'high',
    sports: 'high',
    diversity: 'medium',
    classSize: 'large',
    research: 'high',
    business: 8,
    engineering: 7,
    liberal_arts: 7,
    health: 8,
    undecided: 8,
    cost: 7,
    weather: 'mild',
    homeDistance: 'far',
    transferFriendly: 7,
    description: 'High-energy social culture, strong athletics, and broad academic offerings.'
  },
  {
    name: 'Brown University',
    type: 'private',
    setting: 'urban',
    campusSize: 'small',
    party: 'medium',
    sports: 'low',
    diversity: 'high',
    classSize: 'small',
    research: 'high',
    business: 4,
    engineering: 5,
    liberal_arts: 10,
    health: 5,
    undecided: 9,
    cost: 4,
    weather: 'balanced',
    homeDistance: 'far',
    transferFriendly: 5,
    description: 'Highly collaborative, discussion-based learning and strong emphasis on open intellectual exploration.'
  },
  {
    name: 'Duke University',
    type: 'private',
    setting: 'suburban',
    campusSize: 'medium',
    party: 'medium',
    sports: 'high',
    diversity: 'high',
    classSize: 'small',
    research: 'high',
    business: 7,
    engineering: 8,
    liberal_arts: 8,
    health: 8,
    undecided: 7,
    cost: 3,
    weather: 'balanced',
    homeDistance: 'far',
    transferFriendly: 5,
    description: 'Competitive academics, major school spirit, and a strong residential environment.'
  },
  {
    name: 'University of California, Los Angeles',
    type: 'public',
    setting: 'urban',
    campusSize: 'large',
    party: 'medium',
    sports: 'medium',
    diversity: 'high',
    classSize: 'large',
    research: 'high',
    business: 7,
    engineering: 8,
    liberal_arts: 9,
    health: 8,
    undecided: 9,
    cost: 5,
    weather: 'mild',
    homeDistance: 'far',
    transferFriendly: 6,
    description: 'Powerful academics, strong city access, and broad social and professional opportunities.'
  },
  {
    name: 'Purdue University',
    type: 'public',
    setting: 'suburban',
    campusSize: 'large',
    party: 'medium',
    sports: 'medium',
    diversity: 'medium',
    classSize: 'large',
    research: 'high',
    business: 7,
    engineering: 10,
    liberal_arts: 5,
    health: 5,
    undecided: 7,
    cost: 7,
    weather: 'cold',
    homeDistance: 'moderate',
    transferFriendly: 7,
    description: 'Excellent engineering pipelines and a practical, career-oriented culture.'
  },
  {
    name: 'University of Denver',
    type: 'private',
    setting: 'urban',
    campusSize: 'medium',
    party: 'medium',
    sports: 'medium',
    diversity: 'medium',
    classSize: 'small',
    research: 'medium',
    business: 7,
    engineering: 4,
    liberal_arts: 7,
    health: 6,
    undecided: 7,
    cost: 4,
    weather: 'cold',
    homeDistance: 'moderate',
    transferFriendly: 6,
    description: 'Strong career outcomes, a more polished city setting, and a close-knit campus feel.'
  },
  {
    name: 'Arizona State University',
    type: 'public',
    setting: 'urban',
    campusSize: 'large',
    party: 'medium',
    sports: 'medium',
    diversity: 'high',
    classSize: 'large',
    research: 'high',
    business: 8,
    engineering: 8,
    liberal_arts: 7,
    health: 8,
    undecided: 8,
    cost: 8,
    weather: 'mild',
    homeDistance: 'moderate',
    transferFriendly: 9,
    description: 'Very transfer-friendly, broad option set, and practical access to internships and career connections.'
  }
];

const state = {
  track: null,
  answers: {},
  currentIndex: 0,
  questions: []
};

function renderHome() {
  app.innerHTML = `
    <section class="panel hero">
      <div class="eyebrow">College match engine</div>
      <h1>Find schools that fit your goals, vibe, and future.</h1>
      <p>
        Answer a few quick questions to get a ranked shortlist of colleges that match your academic goals,
        lifestyle, and what matters to you most.
      </p>
      <div class="inline-answers">
        <button class="primary" data-role="start-freshman">I’m a first-time freshman</button>
        <button class="secondary" data-role="start-transfer">I’m a transfer student</button>
      </div>
    </section>
  `;

  document.querySelector('[data-role="start-freshman"]').addEventListener('click', () => startQuiz('freshman'));
  document.querySelector('[data-role="start-transfer"]').addEventListener('click', () => startQuiz('transfer'));
}

function startQuiz(track) {
  state.track = track;
  state.answers = {};
  state.currentIndex = 0;
  state.questions = track === 'freshman' ? freshmanQuestions : transferQuestions;
  renderQuestion();
}

function renderQuestion() {
  const question = state.questions[state.currentIndex];
  const previousAnswer = state.answers[question.id];

  const isMulti = question.type === 'multi';
  const current = question.options
    .map((option) => {
      const selected = isMulti ? (previousAnswer || []).includes(option.value) : previousAnswer === option.value;
      return `
        <button class="choice ${selected ? 'selected' : ''}" data-option="${option.value}" data-multi="${isMulti}">
          <strong>${option.label}</strong>
          ${option.note ? `<small>${option.note}</small>` : ''}
        </button>
      `;
    })
    .join('');

  app.innerHTML = `
    <section class="panel quiz-grid">
      <div class="question-card">
        <div class="question-header">
          <span class="kicker">${state.track === 'freshman' ? 'Freshman track' : 'Transfer track'} • ${state.currentIndex + 1}/${state.questions.length}</span>
          <button class="secondary" id="backBtn">Back</button>
        </div>

        <h2>${question.title}</h2>
        ${question.description ? `<p>${question.description}</p>` : ''}

        <div class="options">${current}</div>

        <div class="actions">
          <div></div>
          <button class="primary" id="nextBtn" ${!previousAnswer || (isMulti && previousAnswer.length === 0) ? 'disabled' : ''}>
            ${state.currentIndex === state.questions.length - 1 ? 'See my matches' : 'Next'}
          </button>
        </div>
      </div>
    </section>
  `;

  document.getElementById('backBtn').addEventListener('click', () => {
    if (state.currentIndex > 0) {
      state.currentIndex -= 1;
      renderQuestion();
    } else {
      renderHome();
    }
  });

  document.querySelectorAll('.choice').forEach((button) => {
    button.addEventListener('click', () => handleChoiceSelection(button));
  });

  document.getElementById('nextBtn').addEventListener('click', () => {
    if (state.currentIndex < state.questions.length - 1) {
      state.currentIndex += 1;
      renderQuestion();
    } else {
      calculateResults();
    }
  });
}

function handleChoiceSelection(button) {
  const optionValue = button.dataset.option;
  const isMulti = button.dataset.multi === 'true';
  const question = state.questions[state.currentIndex];

  if (isMulti) {
    const current = state.answers[question.id] || [];
    const updated = current.includes(optionValue)
      ? current.filter((value) => value !== optionValue)
      : [...current, optionValue];
    state.answers[question.id] = updated;
  } else {
    state.answers[question.id] = optionValue;
  }

  renderQuestion();
}

function calculateResults() {
  const userAnswers = state.answers;
  const scoredSchools = colleges.map((school) => {
    let score = 0;
    const reasons = [];

    if (state.track === 'freshman') {
      const majorMap = {
        engineering: { engineering: 16, undecided: 7, business: 3, health: 4, liberal_arts: 2 },
        business: { business: 14, undecided: 7, engineering: 3, liberal_arts: 4, health: 5 },
        liberal_arts: { liberal_arts: 15, undecided: 8, business: 4, health: 3, engineering: 2 },
        health: { health: 16, undecided: 7, engineering: 3, business: 4, liberal_arts: 2 },
        undecided: { undecided: 12, liberal_arts: 8, engineering: 7, business: 6, health: 6 }
      };

      const major = userAnswers.major || 'undecided';
      score += (school[major] || 0) * 1.2;
      const majorReason = majorMap[major][major] ? 'strong match for your academic direction' : 'broad academic fit';
      reasons.push(majorReason);

      if (userAnswers.classSize === 'small' && school.classSize === 'small') score += 16;
      if (userAnswers.classSize === 'large' && school.classSize === 'large') score += 12;
      if (userAnswers.classSize === 'small' && school.classSize !== 'small') score -= 4;

      if (userAnswers.campusSize === 'small' && school.campusSize === 'small') score += 10;
      if (userAnswers.campusSize === 'large' && school.campusSize === 'large') score += 10;
      if (userAnswers.campusSize === 'small' && school.campusSize === 'large') score -= 4;

      if (userAnswers.setting === school.setting) score += 14;
      if (userAnswers.setting === 'urban' && school.setting === 'urban') score += 7;
      if (userAnswers.setting === 'rural' && school.setting === 'rural') score += 7;

      if (userAnswers.partyCulture === 'high' && school.party === 'high') score += 12;
      if (userAnswers.partyCulture === 'low' && school.party === 'low') score += 8;
      if (userAnswers.partyCulture === 'high' && school.party === 'low') score -= 8;

      if (userAnswers.sports === 'high' && school.sports === 'high') score += 10;
      if (userAnswers.sports === 'low' && school.sports === 'low') score += 7;

      if (userAnswers.diversity === 'important' && school.diversity === 'high') score += 12;
      if (userAnswers.diversity === 'not' && school.diversity === 'low') score += 6;

      if (userAnswers.budget === 'instate' && school.type === 'public') score += 10;
      if (userAnswers.budget === 'aid' && school.cost >= 7) score += 12;
      if (userAnswers.budget === 'flexible' && school.cost >= 5) score += 8;

      if (userAnswers.weather === school.weather) score += 8;
      if (userAnswers.weather === 'mild' && school.weather === 'mild') score += 8;
      if (userAnswers.weather === 'cold' && school.weather === 'cold') score += 8;

      if (userAnswers.homeDistance === 'close' && school.homeDistance === 'close') score += 8;
      if (userAnswers.homeDistance === 'far' && school.homeDistance === 'far') score += 8;
      if (userAnswers.homeDistance === 'far' && school.homeDistance === 'moderate') score += 5;

      if (userAnswers.major === 'engineering' && school.engineering >= 9) score += 12;
      if (userAnswers.major === 'business' && school.business >= 8) score += 12;
      if (userAnswers.major === 'liberal_arts' && school.liberal_arts >= 9) score += 12;
      if (userAnswers.major === 'health' && school.health >= 8) score += 12;

      if (school.research === 'high' && userAnswers.major !== 'business') score += 5;
      if (school.classSize === 'small' && userAnswers.classSize === 'small') score += 6;
      if (school.sports === 'high' && userAnswers.sports === 'high') score += 5;

      if (userAnswers.partyCulture === 'low' && school.party === 'high') score -= 10;
      if (userAnswers.sports === 'low' && school.sports === 'high') score -= 5;
      if (userAnswers.campusSize === 'small' && school.campusSize === 'large') score -= 7;
    }

    if (state.track === 'transfer') {
      score += school.transferFriendly * 1.8;
      reasons.push('transfer-friendly support is a plus');

      const painPoints = userAnswers.painPoints || [];
      if (painPoints.includes('too_big') && school.campusSize === 'large') score -= 18;
      if (painPoints.includes('too_small') && school.campusSize === 'small') score -= 14;
      if (painPoints.includes('no_party') && school.party === 'low') score -= 16;
      if (painPoints.includes('party_too_much') && school.party === 'high') score -= 12;
      if (painPoints.includes('too_far') && school.setting === 'rural') score -= 12;
      if (painPoints.includes('too_close') && school.homeDistance === 'close') score -= 10;
      if (painPoints.includes('weak_major') && school[ userAnswers.major || 'undecided' ] < 7) score -= 18;
      if (painPoints.includes('too_expensive') && school.cost <= 5) score -= 12;
      if (painPoints.includes('cliquey') && school.diversity === 'low') score -= 13;
      if (painPoints.includes('bad_advising') && school.transferFriendly <= 5) score -= 12;
      if (painPoints.includes('wrong_location') && school.setting === userAnswers.setting) score -= 10;

      if (userAnswers.transferReason === 'cost' && school.cost >= 7) score += 18;
      if (userAnswers.transferReason === 'major' && school[userAnswers.major || 'undecided'] >= 8) score += 18;
      if (userAnswers.transferReason === 'home' && school.homeDistance === 'close') score += 14;
      if (userAnswers.transferReason === 'better_fit' && school.setting === userAnswers.setting) score += 12;
      if (userAnswers.transferPriority === 'credit_transfer' && school.transferFriendly >= 8) score += 16;
      if (userAnswers.transferPriority === 'location' && school.setting === userAnswers.setting) score += 10;
    }

    if (state.track === 'transfer' && userAnswers.transferPriority === 'credit_transfer') {
      if (school.transferFriendly >= 8) {
        score += 8;
      }
    }

    return { school, score, reasons: Array.from(new Set(reasons)).slice(0, 3) };
  });

  const ranked = scoredSchools
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map((entry) => {
      const max = 220;
      const percentage = Math.max(55, Math.min(98, Math.round((entry.score / max) * 100)));
      return { ...entry, percentage };
    });

  renderResults(ranked);
}

function renderResults(matches) {
  const answers = state.answers;
  const summaryItems = [
    state.track === 'freshman' ? `Major interest: ${answers.major || 'Undecided'}` : `Transfer reason: ${answers.transferReason || 'Not specified'}`,
    state.track === 'freshman' ? `Campus vibe: ${answers.setting || 'Flexible'}` : `Pain points: ${(answers.painPoints || []).length || 0} selected`,
    state.track === 'freshman' ? `Priority: ${answers.budget || 'Flexible cost'}` : `Transfer priority: ${answers.transferPriority || 'Flexible'}`
  ];

  app.innerHTML = `
    <section class="panel results">
      <div class="summary-card">
        <h3>Your best-fit shortlist</h3>
        <ul class="summary-list">
          ${summaryItems.map((item) => `<li>${item}</li>`).join('')}
        </ul>
        <div class="badge-row" style="margin-top: 14px;">
          <span class="badge">Top 5 matches</span>
          <span class="badge">Explainable rankings</span>
          <span class="badge">Adjustable weights</span>
        </div>
      </div>

      <div class="match-list">
        ${matches.length
          ? matches
              .map(
                (match) => `
                  <article class="match-card">
                    <div class="match-header">
                      <div class="school-name">${match.school.name}</div>
                      <div class="score-pill">${match.percentage}% match</div>
                    </div>
                    <div class="match-meta">${match.school.setting} • ${match.school.campusSize} campus • ${match.school.party} party energy</div>
                    <p class="explanation">
                      ${match.school.description}
                      ${match.reasons.length ? ` Reasons: ${match.reasons.join(', ')}.` : ''}
                    </p>
                    <div class="badge-row">
                      <span class="badge">${match.school.type}</span>
                      <span class="badge">Research: ${match.school.research}</span>
                      <span class="badge">Transfer-friendly: ${match.school.transferFriendly}/10</span>
                    </div>
                  </article>
                `
              )
              .join('')
          : `<div class="empty-state">No matches yet. Try adjusting your answers.</div>`}
      </div>
    </section>
  `;

  retakeBtn.classList.remove('hidden');
  retakeBtn.onclick = () => renderHome();
}

retakeBtn.addEventListener('click', () => renderHome());
renderHome();
