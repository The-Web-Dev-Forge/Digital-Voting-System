// Simple simulated AI tutor widget (compact toggle + wholesome canned responses)
(function(){
    function createMessage(text, from='bot'){
        const el = document.createElement('div');
        el.className = 'ai-message ' + (from==='bot' ? 'ai-bot' : 'ai-user');
        el.textContent = text;
        return el;
    }

    function showOptions(options){
        const container = document.getElementById('aiOptions');
        if(!container) return;
        container.innerHTML = '';
        if(!options || !options.length) return;
        options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'ai-option-btn';
            btn.type = 'button';
            btn.textContent = opt;
            btn.addEventListener('click', () => handleOption(opt));
            container.appendChild(btn);
        });
    }

    function scrollMessages(){
        // scroll the combined scrollable container so messages and options remain visible
        const container = document.getElementById('aiScrollContainer') || document.getElementById('aiMessages');
        if(!container) return;
        container.scrollTop = container.scrollHeight;
    }

    function botReply(text){
        const msgs = document.getElementById('aiMessages');
        if(!msgs) return;
        msgs.appendChild(createMessage(text, 'bot'));
        scrollMessages();
    }

    function handleGreeting(){
        botReply('Hey there! I\'m here to help — what would you like to know from these options?');
        if(window.__aiTutorOptionsForPage) showOptions(window.__aiTutorOptionsForPage);
    }

    function handleOption(option){
        const msgs = document.getElementById('aiMessages');
        if(!msgs) return;
        msgs.appendChild(createMessage(option, 'user'));
        scrollMessages();

        setTimeout(() => {
            let resp = '';
            // Wholesome, helpful canned responses tailored for registration and related flows
            if(/eligibility|who can vote/i.test(option)){
                resp = 'Eligibility: You must be an Indian citizen and at least 18 years old on the qualifying date. If you\'re unsure about special cases (NRIs, service voters), I can explain those too.';
            } else if(/registration|register|steps|how to fill/i.test(option)){
                resp = 'Registration steps (quick): 1) Complete the registration form carefully using your official ID details, 2) Upload clear copies of required documents and a recent passport photo, 3) Submit and note the reference number, 4) Wait for ERO/BLO verification, 5) Receive confirmation and EPIC. Want a printable checklist or an on-screen step-by-step guide?';
            } else if(/required documents|documents|formats|checklist/i.test(option)){
                resp = 'Document checklist: primary ID (Aadhaar/passport/driving licence), proof of address (if different), and a recent passport-size photo. Make sure scans/photos are clear (no blur), upright, and include all corners. Typical accepted formats: JPG, PNG, PDF; size usually <= 2MB.';
            } else if(/photo|upload|image/i.test(option)){
                resp = 'Photo & upload tips: Use a plain light background, face centered, neutral expression, good lighting, and avoid shadows. Head should fill ~70% of the frame. Save as JPG/PNG and keep file size under 2MB. If your photo is too large, I can suggest safe resize tools.';
            } else if(/federated.*(privacy|learning)|privacy.*federated/i.test(option)){
                resp = '🔒 <strong>Your Privacy is Protected with Federated Learning!</strong><br><br>' +
                    '<strong>How it works:</strong><br>' +
                    '1️⃣ <strong>Local Processing:</strong> Your face photo is analyzed entirely on YOUR device (phone/computer)<br>' +
                    '2️⃣ <strong>No Raw Images Sent:</strong> We NEVER receive your actual photo - only mathematical features<br>' +
                    '3️⃣ <strong>Encrypted Transmission:</strong> Even the features are encrypted before leaving your device<br>' +
                    '4️⃣ <strong>Federated Training:</strong> If you consent, your device helps improve accuracy WITHOUT sharing your data<br>' +
                    '5️⃣ <strong>Differential Privacy:</strong> Any updates from your device have mathematical noise added for extra protection<br><br>' +
                    '<strong>What we DON\'T store:</strong><br>' +
                    '❌ Your face photo<br>' +
                    '❌ Identifiable biometric data<br>' +
                    '❌ Personal images<br><br>' +
                    '<strong>What we DO store:</strong><br>' +
                    '✅ Encrypted mathematical embeddings (meaningless without your device)<br>' +
                    '✅ Verification results (for audit)<br>' +
                    '✅ Aggregated model improvements (from many users, privacy-protected)<br><br>' +
                    '<em>Your biometric data stays on YOUR device. Always.</em>';
                showOptions(['How is this different from traditional systems?', 'Can I opt out of federated training?', 'What data is actually shared?', 'Technical details', 'Back to main options']);
            } else if(/different.*traditional|traditional.*different|vs traditional/i.test(option)){
                resp = '<strong>Federated Learning vs Traditional Biometric Systems:</strong><br><br>' +
                    '<table style="width:100%; border-collapse: collapse; font-size:13px;">' +
                    '<tr style="background:#f0f0f0;"><th style="padding:8px; border:1px solid #ddd;">Aspect</th><th style="padding:8px; border:1px solid #ddd;">Traditional</th><th style="padding:8px; border:1px solid #ddd;">Our System (Federated)</th></tr>' +
                    '<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Data Storage</strong></td><td style="padding:8px; border:1px solid #ddd;">❌ Raw photos stored on server</td><td style="padding:8px; border:1px solid #ddd;">✅ Only encrypted embeddings</td></tr>' +
                    '<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Processing Location</strong></td><td style="padding:8px; border:1px solid #ddd;">❌ Server-side (centralized)</td><td style="padding:8px; border:1px solid #ddd;">✅ Your device (decentralized)</td></tr>' +
                    '<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Privacy Risk</strong></td><td style="padding:8px; border:1px solid #ddd;">❌ High (data breach = face exposure)</td><td style="padding:8px; border:1px solid #ddd;">✅ Low (breach = encrypted math only)</td></tr>' +
                    '<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Model Training</strong></td><td style="padding:8px; border:1px solid #ddd;">❌ Requires collecting all data</td><td style="padding:8px; border:1px solid #ddd;">✅ Trains without seeing your data</td></tr>' +
                    '<tr><td style="padding:8px; border:1px solid #ddd;"><strong>User Control</strong></td><td style="padding:8px; border:1px solid #ddd;">❌ Limited control</td><td style="padding:8px; border:1px solid #ddd;">✅ Full control (opt-in/out anytime)</td></tr>' +
                    '</table><br>' +
                    '<em>Federated Learning = Maximum security + Better accuracy + Your privacy guaranteed</em>';
                showOptions(['Can I opt out of federated training?', 'What data is actually shared?', 'Technical details', 'Back to federated privacy info']);
            } else if(/opt.*(out|in)|disable.*federated|consent/i.test(option)){
                resp = '<strong>Federated Training Consent - YOU\'RE IN CONTROL</strong><br><br>' +
                    '✅ <strong>Default:</strong> Your device can participate in improving model accuracy (privacy-protected)<br>' +
                    '❌ <strong>Opt-Out:</strong> You can disable federated training anytime<br><br>' +
                    '<strong>Even if you participate:</strong><br>' +
                    '• Your raw biometric data NEVER leaves your device<br>' +
                    '• Only differential-privacy protected mathematical updates are shared<br>' +
                    '• No one (including us) can reverse-engineer your face from the updates<br>' +
                    '• You help improve accuracy for all voters while staying anonymous<br><br>' +
                    '<strong>To manage your consent:</strong><br>' +
                    'Click the button below or visit Settings > Privacy > Federated Learning<br><br>' +
                    '<button onclick="toggleFederatedConsent()" style="padding:10px 15px; background:#3498db; color:white; border:none; border-radius:5px; cursor:pointer; font-size:14px;">' +
                    '⚙️ Manage Consent Settings' +
                    '</button>';
                showOptions(['What data is actually shared?', 'How is this different from traditional systems?', 'Technical details', 'Back to main options']);
            } else if(/what.*shared|data.*shared|actually.*sent/i.test(option)){
                resp = '<strong>What Data Is Actually Shared?</strong><br><br>' +
                    '📊 <strong>When you register biometric data:</strong><br>' +
                    '• Encrypted 128-dimensional mathematical vector (NOT your photo)<br>' +
                    '• Confidence score (e.g., 95% face detection confidence)<br>' +
                    '• Timestamp<br><br>' +
                    '🔄 <strong>If you consent to federated training:</strong><br>' +
                    '• Differential-privacy protected gradient updates<br>' +
                    '• Number of local samples used<br>' +
                    '• Training loss metric<br><br>' +
                    '❌ <strong>What is NEVER shared:</strong><br>' +
                    '• Your face photo (processed 100% locally)<br>' +
                    '• Raw biometric features<br>' +
                    '• Personal identifying information in training data<br>' +
                    '• Anything that could be used to reconstruct your face<br><br>' +
                    '🛡️ <strong>Privacy Protection:</strong><br>' +
                    'Laplacian noise is added to all gradient updates (differential privacy with ε=1.0).<br>' +
                    'This makes it mathematically impossible to extract individual biometric data.';
                showOptions(['Technical details about differential privacy', 'How encryption works', 'Back to federated privacy info']);
            } else if(/technical|differential.*privacy|how.*works|encryption/i.test(option)){
                resp = '<strong>🔬 Technical Details - Federated Learning Privacy</strong><br><br>' +
                    '<strong>1. Client-Side Processing:</strong><br>' +
                    '• TensorFlow.js + FaceAPI runs in your browser<br>' +
                    '• Face detection → 128-d embedding extraction (FaceNet-style)<br>' +
                    '• Processing time: ~200-500ms on modern devices<br><br>' +
                    '<strong>2. Encryption:</strong><br>' +
                    '• AES-256-GCM for embedding encryption<br>' +
                    '• Random IV (Initialization Vector) per encryption<br>' +
                    '• Web Crypto API (browser-native, secure)<br><br>' +
                    '<strong>3. Differential Privacy (ε=1.0):</strong><br>' +
                    '• Laplacian mechanism for gradient perturbation<br>' +
                    '• Sensitivity: 0.1 (L2 norm of gradients)<br>' +
                    '• Noise: Lap(0, 0.1/ε) added to each gradient component<br><br>' +
                    '<strong>4. Federated Averaging (FedAvg):</strong><br>' +
                    '• Server aggregates ≥10 client contributions<br>' +
                    '• Weighted average by number of local samples<br>' +
                    '• No individual gradient inspection possible<br><br>' +
                    '<strong>5. Security Properties:</strong><br>' +
                    '• Privacy loss budget: ε=1.0 (strong privacy)<br>' +
                    '• Membership inference attack resistance<br>' +
                    '• Model inversion attack protection<br><br>' +
                    '<em>Standards: GDPR compliant, follows Google\'s Federated Learning best practices</em>';
                showOptions(['What is differential privacy in simple terms?', 'How secure is this really?', 'Back to federated privacy info']);
            } else if(/verification|face detection|privacy/i.test(option)){
                resp = 'Verification & privacy: Face-detection may be used for liveness checks during verification — it helps confirm you are a real person. With our federated learning system, all face analysis happens ON YOUR DEVICE. Images are used only for verification and handled per the site\'s privacy policy. If you have privacy concerns, you can request manual/in-person verification via your local ERO.';
            } else if(/after submission|what to expect|next steps|form submission/i.test(option)){
                resp = 'After submission: Your application will be reviewed by the local ERO. You may receive SMS/email updates asking for clarifications or additional documents. Keep your reference number handy; it speeds up support requests. Once approved, you\'ll be added to the roll and can vote.';
            } else if(/nri/i.test(option)){
                resp = 'NRI Support: NRIs typically use Form 6A. You will need a valid passport copy and proof of overseas residence. Voting rules for NRIs can change, so check the latest official guidance or ask me to fetch the steps.';
            } else if(/accessibility|support|help/i.test(option)){
                resp = 'Accessibility & support: If you need help filling the form, call the toll-free number (1950) or visit your local ERO office. Tell me what help you need (e.g., large text, screen reader tips) and I\'ll suggest options.';
            } else if(/how to apply|apply/i.test(option)){
                resp = 'To apply online: click Register, fill details exactly as shown on your ID, attach clear scans, and submit. You\'ll get a reference number — save it. If you prefer, I can walk you through each field now.';
            } else if(/more details|details/i.test(option)){
                resp = 'I can give a detailed checklist, explain upload sizes and formats, or walk you through each form field step-by-step. Which would you like?';
            } else if(/back to main|main options/i.test(option)){
                resp = 'Back to main options — choose any topic above or type your specific question.';
            } else {
                resp = 'I can help with filling the form, required documents, photo & uploads, verification & privacy, next steps after submission, and accessibility. Which one should I explain?';
            }

            botReply(resp);
            // follow-ups tailored to registration flow
            showOptions(['How to fill the registration form','Required documents & formats','Photo & upload help','Privacy & face verification','Form submission & next steps','Accessibility & support','Contact support / Toll-free 1950']);
        }, 550);
    }

    function handleUserInput(raw){
        const text = (raw||'').trim();
        if(!text) return;
        const msgs = document.getElementById('aiMessages');
        if(!msgs) return;
        msgs.appendChild(createMessage(text, 'user'));
        scrollMessages();

        if(/^(hi|hello|hey)\b/i.test(text)){
            handleGreeting();
            return;
        }

        // otherwise attempt to match known topics first
        handleOption(text);
    }

    function openPanel(){
        const panel = document.getElementById('aiTutorPanel');
        const input = document.getElementById('aiInput');
        if(panel){ panel.style.display = ''; }
        if(input) input.focus();
        if(window.__aiTutorOptionsForPage) showOptions(window.__aiTutorOptionsForPage);
    }

    function closePanel(){
        const panel = document.getElementById('aiTutorPanel');
        if(panel) panel.style.display = 'none';
    }

    function init(){
        const toggle = document.getElementById('aiTutorToggle');
        const closeBtn = document.getElementById('aiTutorClose');
        const send = document.getElementById('aiSend');
        const input = document.getElementById('aiInput');

        if(toggle) toggle.addEventListener('click', openPanel);
        if(closeBtn) closeBtn.addEventListener('click', closePanel);
        if(send) send.addEventListener('click', () => { handleUserInput(input.value); input.value = ''; });
        if(input) input.addEventListener('keydown', (e) => { if(e.key === 'Enter'){ e.preventDefault(); handleUserInput(input.value); input.value=''; }});

        // warm welcome message
        const msgs = document.getElementById('aiMessages');
        if(msgs) msgs.appendChild(createMessage('Welcome — I\'m your friendly AI Tutor. Type hi or choose a topic to get started.', 'bot'));
        scrollMessages();
    }

    window.initAiTutor = function(options){
        try{ window.__aiTutorOptionsForPage = options || []; } catch(e){ window.__aiTutorOptionsForPage = []; }
        // initialize when the panel exists on the page
        if(document.getElementById('aiTutorToggle')){
            init();
            // show options only after panel opens; but we can pre-populate
            if(window.__aiTutorOptionsForPage && document.getElementById('aiOptions')){
                // do not auto-show until user opens; keep available
            }
        }
    };

})();
