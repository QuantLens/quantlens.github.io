(function(){
  const yearEl = document.getElementById('year');
  if(yearEl) yearEl.textContent = new Date().getFullYear();

  const sample = document.getElementById('sample-json')?.textContent.trim();
  const jsonTA = document.getElementById('json');
  const tplTA = document.getElementById('tpl');

  const basePrompt = `You are a pro technical analyst. Read the QuantLens JSON and produce:
1) 1-paragraph market state.
2) Trend by horizon (short/medium/long).
3) Momentum & volatility (SMA/EMA, RSI, ATR%, HV, BB position).
4) VP-Lite (POC/VAL/VAH, acceptance, regime) and implications.
5) Levels (support/resistance, fib) with specific prices.
6) Scenarios/signals (triggers, invalids, stops, TPs, RR).
7) Risk section (sizing via ATR, failure modes).
8) Actionable plan: bull, bear, range.
9) Be ready to answer follow-ups from the same context.
Rules: Use numbers as given; don’t invent fields not present. If a block is missing, say “not provided” and continue.
Payload follows:`;

  if(tplTA){ tplTA.value = basePrompt; }

  document.querySelector('[data-load-sample]')?.addEventListener('click', ()=>{
    if(jsonTA){ jsonTA.value = sample || ''; jsonTA.focus(); }
  });
  document.querySelector('[data-clear]')?.addEventListener('click', ()=>{
    if(jsonTA){ jsonTA.value=''; jsonTA.focus(); }
  });

  const copy = async (text)=>{
    try{ await navigator.clipboard.writeText(text); toast('Copied'); }catch(e){ console.warn(e); }
  };

  document.querySelector('[data-copy-tpl]')?.addEventListener('click', ()=>{
    copy(tplTA?.value || basePrompt);
  });
  document.querySelector('[data-copy-all]')?.addEventListener('click', ()=>{
    const j = jsonTA?.value?.trim() || '';
    const joined = j ? basePrompt + "\n\n" + j : basePrompt;
    copy(joined);
  });

  document.querySelector('[data-copy-sample-email]')?.addEventListener('click', ()=>{
    const text = document.getElementById('sample-email')?.textContent || '';
    copy(text.trim());
  });

  document.querySelector('[data-copy-llm-output]')?.addEventListener('click', ()=>{
    const text = document.getElementById('sample-llm-output')?.textContent || '';
    copy(text.trim());
  });

  // Generic copy buttons using data-copy-target
  document.querySelectorAll('[data-copy-target]')?.forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const sel = btn.getAttribute('data-copy-target');
      if(!sel) return;
      const el = document.querySelector(sel);
      if(!el) return;
      const text = el.textContent || '';
      copy(text.trim());
    });
  });

  // Tabs behavior
  document.querySelectorAll('[data-tabs]')?.forEach(tabRoot=>{
    const buttons = tabRoot.querySelectorAll('.tabs__btn');
    const panels = tabRoot.querySelectorAll('.tabs__panel');
    buttons.forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const tab = btn.getAttribute('data-tab');
        if(!tab) return;
        buttons.forEach(b=>b.classList.toggle('is-active', b===btn));
        panels.forEach(p=>{
          p.classList.toggle('is-active', p.getAttribute('data-panel')===tab);
        });
      });
    });
  });

  function toast(msg){
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(()=>{ t.classList.add('show'); }, 10);
    setTimeout(()=>{ t.classList.remove('show'); t.remove(); }, 2000);
  }
})();
