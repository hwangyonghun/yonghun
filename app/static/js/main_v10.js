document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadContent = document.getElementById('upload-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultOverlay = document.getElementById('result-overlay');
    const resetBtn = document.getElementById('reset-btn');

    let currentFile = null;
    let activeMode = 'upload'; // 'upload' or 'url'

    // Tab Switching
    const tabs = document.querySelectorAll('.tab-btn');
    const urlZone = document.getElementById('url-zone');
    const marketingZone = document.getElementById('marketing-zone');
    const trackingZone = document.getElementById('tracking-zone');
    const urlInput = document.getElementById('youtube-url');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Deactivate all
            tabs.forEach(t => t.classList.remove('active'));
            // Activate click
            tab.classList.add('active');

            activeMode = tab.dataset.tab;

            // Reset UI
            dropZone.classList.add('hidden');
            urlZone.classList.add('hidden');
            if (marketingZone) marketingZone.classList.add('hidden');
            if (trackingZone) trackingZone.classList.add('hidden');
            analyzeBtn.classList.add('hidden');

            if (activeMode === 'upload') {
                dropZone.classList.remove('hidden');
                if (currentFile) analyzeBtn.classList.remove('hidden');
            } else if (activeMode === 'url') {
                urlZone.classList.remove('hidden');
                if (urlInput.value.trim()) analyzeBtn.classList.remove('hidden');
            } else if (activeMode === 'marketing') {
                if (marketingZone) marketingZone.classList.remove('hidden');
            } else if (activeMode === 'tracking') {
                if (trackingZone) trackingZone.classList.remove('hidden');
            }
        });
    });

    // Marketing Logic
    const createPromoBtn = document.getElementById('create-promo-btn');
    const uploadYtBtn = document.getElementById('upload-yt-btn');
    const promoStatus = document.getElementById('promo-status');

    if (createPromoBtn) {
        createPromoBtn.addEventListener('click', async () => {
            createPromoBtn.disabled = true;
            createPromoBtn.innerHTML = '<span class="loader"></span> Generating...';

            try {
                const response = await fetch('/api/create-promo', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    promoStatus.textContent = 'Video Created Successfully!';
                    promoStatus.classList.remove('hidden');
                    uploadYtBtn.classList.remove('hidden');
                    if (document.getElementById('upload-insta-btn'))
                        document.getElementById('upload-insta-btn').classList.remove('hidden');
                    if (document.getElementById('upload-tiktok-btn'))
                        document.getElementById('upload-tiktok-btn').classList.remove('hidden');

                    // Auto download
                    // window.location.href = data.file_url;
                } else {
                    alert('Error creating video: ' + (data.error || 'Unknown error'));
                }
            } catch (e) {
                console.error(e);
                alert('Connection error');
            } finally {
                createPromoBtn.disabled = false;
                createPromoBtn.innerHTML = '<i class="fa-solid fa-video"></i> Generate Promo Video';
            }
        });
    }

    if (uploadYtBtn) {
        uploadYtBtn.addEventListener('click', async () => {
            uploadYtBtn.disabled = true;
            uploadYtBtn.innerHTML = '<span class="loader"></span> Authorizing...';

            try {
                const response = await fetch('/api/upload-youtube', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    alert(data.message + '\n\n' + data.info);
                } else {
                    alert('Upload failed');
                }
            } catch (e) {
                console.error(e);
                alert('Connection error');
            } finally {
                uploadYtBtn.disabled = false;
                uploadYtBtn.innerHTML = '<i class="fa-brands fa-youtube"></i> Upload to YouTube';
            }
        });
    }

    const uploadInstaBtn = document.getElementById('upload-insta-btn');
    if (uploadInstaBtn) {
        uploadInstaBtn.addEventListener('click', async () => {
            uploadInstaBtn.disabled = true;
            uploadInstaBtn.innerHTML = '<span class="loader"></span> Posting...';

            try {
                const response = await fetch('/api/upload-instagram', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                    window.open('https://www.instagram.com/reels/create/', '_blank');
                } else {
                    alert('Upload failed');
                }
            } catch (e) {
                console.error(e);
                alert('Connection error');
            } finally {
                uploadInstaBtn.disabled = false;
                uploadInstaBtn.innerHTML = '<i class="fa-brands fa-instagram"></i> Upload to Instagram Reels';
            }
        });
    }

    const uploadTikTokBtn = document.getElementById('upload-tiktok-btn');
    if (uploadTikTokBtn) {
        uploadTikTokBtn.addEventListener('click', async () => {
            uploadTikTokBtn.disabled = true;
            uploadTikTokBtn.innerHTML = '<span class="loader"></span> Posting...';

            try {
                const response = await fetch('/api/upload-tiktok', { method: 'POST' });
                const data = await response.json();

                if (response.ok) {
                    alert(data.message);
                } else {
                    alert('Upload failed');
                }
            } catch (e) {
                console.error(e);
                alert('Connection error');
            } finally {
                uploadTikTokBtn.disabled = false;
                uploadTikTokBtn.innerHTML = '<i class="fa-brands fa-tiktok" style="color: #00f2ea;"></i> <span style="margin-left:5px; color: #ff0050;">Upload to TikTok</span>';
            }
        });
    }

    // URL Input Listener
    urlInput.addEventListener('input', () => {
        if (urlInput.value.trim().length > 0) {
            analyzeBtn.classList.remove('hidden');
        } else {
            analyzeBtn.classList.add('hidden');
        }
    });


    // Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        if (dropZone) dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        if (dropZone) dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        if (dropZone) dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    if (dropZone) {
        dropZone.addEventListener('drop', handleDrop, false);
        dropZone.addEventListener('click', (e) => {
            if (e.target !== removeBtn && !removeBtn.contains(e.target)) {
                fileInput.click();
            }
        });
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            currentFile = files[0];
            // Validate type
            if (!currentFile.type.startsWith('image/') &&
                currentFile.type !== 'application/pdf' &&
                !currentFile.type.startsWith('video/')) {
                alert('Please upload an image, PDF, or video file.');
                currentFile = null;
                return;
            }
            showPreview(currentFile);
        }
    }

    function showPreview(file) {
        if (file.type === 'application/pdf') {
            imagePreview.src = '';
            imagePreview.classList.add('hidden');
            let pdfIcon = document.getElementById('pdf-preview-icon');
            if (!pdfIcon) {
                pdfIcon = document.createElement('div');
                pdfIcon.id = 'pdf-preview-icon';
                pdfIcon.innerHTML = '<i class="fa-solid fa-file-pdf" style="font-size: 5rem; color: #ef4444;"></i>';
                previewContainer.insertBefore(pdfIcon, imagePreview);
            }
            pdfIcon.classList.remove('hidden');
        } else if (file.type.startsWith('video/')) {
            imagePreview.src = '';
            imagePreview.classList.add('hidden');
            let vidIcon = document.getElementById('vid-preview-icon');
            if (!vidIcon) {
                vidIcon = document.createElement('div');
                vidIcon.id = 'vid-preview-icon';
                vidIcon.innerHTML = `<i class="fa-solid fa-file-video" style="font-size: 5rem; color: #3b82f6;"></i><p style="margin-top:10px">${file.name}</p>`;
                previewContainer.insertBefore(vidIcon, imagePreview);
            }
            vidIcon.innerHTML = `<i class="fa-solid fa-file-video" style="font-size: 5rem; color: #3b82f6;"></i><p style="margin-top:10px">${file.name}</p>`;
            vidIcon.classList.remove('hidden');
        } else {
            // Image handling
            const pdfIcon = document.getElementById('pdf-preview-icon');
            if (pdfIcon) pdfIcon.classList.add('hidden');
            const vidIcon = document.getElementById('vid-preview-icon');
            if (vidIcon) vidIcon.classList.add('hidden');

            imagePreview.classList.remove('hidden');

            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onloadend = function () {
                imagePreview.src = reader.result;
            }
        }

        uploadContent.classList.add('hidden');
        previewContainer.classList.remove('hidden');
        analyzeBtn.classList.remove('hidden');
    }

    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    function resetUpload() {
        currentFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        urlInput.value = '';
        uploadContent.classList.remove('hidden');
        previewContainer.classList.add('hidden');

        // Hide icons
        const pdfIcon = document.getElementById('pdf-preview-icon');
        if (pdfIcon) pdfIcon.classList.add('hidden');
        const vidIcon = document.getElementById('vid-preview-icon');
        if (vidIcon) vidIcon.classList.add('hidden');

        analyzeBtn.classList.add('hidden');
        resultOverlay.classList.remove('active');
    }

    // Analysis
    analyzeBtn.addEventListener('click', async () => {
        if (activeMode === 'upload' && !currentFile) return;
        if (activeMode === 'url' && !urlInput.value.trim()) return;

        setLoading(true);

        const formData = new FormData();
        const lang = document.getElementById('language-select').value;
        formData.append('lang', lang);

        if (activeMode === 'upload') {
            formData.append('file', currentFile);
        } else {
            formData.append('url', urlInput.value.trim());
        }

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });


            const data = await response.json();

            if (response.ok) {
                showResult(data);
            } else {
                console.error("Server Error:", data);
                showError(data.error || "Server returned an error");
            }
        } catch (error) {
            console.error('Error:', error);
            showError("Network or server error occurred. Please check console.");
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        const btnText = analyzeBtn.querySelector('.btn-text');
        const loader = analyzeBtn.querySelector('.loader');

        analyzeBtn.disabled = isLoading;
        if (isLoading) {
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
        } else {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    }

    function showError(message) {
        const verdictIcon = document.getElementById('verdict-icon');
        const verdictText = document.getElementById('verdict-text');

        // Reset and show error state in result card
        verdictIcon.className = 'verdict-icon';
        verdictIcon.innerHTML = '<i class="fa-solid fa-circle-exclamation" style="color: var(--danger)"></i>';

        verdictText.textContent = "ERROR";
        verdictText.style.color = 'var(--danger)';

        const cardReq = document.querySelector('.confidence-meter');
        if (cardReq) cardReq.style.display = 'none';

        // Add error message
        let errorMsg = document.getElementById('error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('p');
            errorMsg.id = 'error-message';
            errorMsg.style.color = 'var(--text-muted)';
            errorMsg.style.marginTop = '1rem';
            document.querySelector('.result-card').appendChild(errorMsg);
        }
        errorMsg.textContent = message;
        errorMsg.style.display = 'block';

        resultOverlay.classList.add('active');
    }

    function showResult(data) {
        const verdictIcon = document.getElementById('verdict-icon');
        const verdictText = document.getElementById('verdict-text');
        const confidenceBar = document.getElementById('confidence-bar');
        const confidenceValue = document.getElementById('confidence-value');
        const explanationEl = document.getElementById('explanation-text');

        const probability = typeof data.probability === 'number'
            ? data.probability
            : 0;

        verdictIcon.className = 'verdict-icon';

        // Use server provided localized text
        if (data.is_fake) {
            verdictIcon.classList.add('verdict-fake');
            verdictIcon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
            verdictText.textContent = data.verdict_text || "DEEPFAKE DETECTED";
            verdictText.style.color = 'var(--danger)';
            confidenceBar.style.backgroundColor = 'var(--danger)';
        } else {
            verdictIcon.classList.add('verdict-real');
            verdictIcon.innerHTML = '<i class="fa-solid fa-check-circle"></i>';
            verdictText.textContent = data.verdict_text || "LIKELY REAL";
            verdictText.style.color = 'var(--success)';
            confidenceBar.style.backgroundColor = 'var(--success)';
        }


        // Animation for bar
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            confidenceBar.style.width = (data.probability * 100) + '%';
        }, 100);

        confidenceValue.textContent = (data.probability * 100).toFixed(1) + '%';

        if (explanationEl && data.explanation) {
            explanationEl.textContent = data.explanation;
        }

        // Add Premium Certificate Button
        const existingCertBtn = document.getElementById('cert-btn');
        if (existingCertBtn) existingCertBtn.remove();

        const certBtn = document.createElement('button');
        certBtn.id = 'cert-btn';
        certBtn.className = 'cta-btn';
        certBtn.style.marginTop = '1rem';
        certBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)'; // Green gradient
        certBtn.innerHTML = `<i class="fa-solid fa-certificate"></i> ${getT('btn_certificate')}`;

        certBtn.addEventListener('click', tryDownloadCertificate);

        const resultCard = document.getElementById('result-card');
        const resetBtn = document.getElementById('reset-btn');
        resultCard.insertBefore(certBtn, resetBtn);

        resultOverlay.classList.add('active');
    }

    async function tryDownloadCertificate() {
        const certBtn = document.getElementById('cert-btn');
        const originalText = certBtn.innerHTML;
        certBtn.innerHTML = `<span class="loader" style="width: 20px; height: 20px; border-width: 2px;"></span> ${getT('msg_checking')}`;
        certBtn.disabled = true;

        try {
            // Attempt to get certificate
            const lang = document.getElementById('language-select').value;
            const response = await fetch(`/api/certificate?lang=${lang}`);

            if (response.ok) {
                // Free limit logic passed, download blob
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                // Open PDF in new tab for printing
                const pdfWindow = window.open(url, '_blank');
                if (!pdfWindow) {
                    alert('Pop-up blocked. Please allow pop-ups to view and print the certificate.');
                    // Fallback to download so they still get it
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = 'Toubina_Certificate.pdf';
                    document.body.appendChild(a);
                    a.click();
                } else {
                    // Slight timeout to revoke url not appropriate if window uses it? 
                    // Actually usually fine for blob urls once loaded.
                }
                alert('Certificate downloaded successfully (Free Tier).');
            } else if (response.status === 403) {
                // Limit reached
                const data = await response.json();
                alert(data.message || 'Free limit reached.');
                openPaymentModal();
            } else {
                alert('Error generating certificate. Please try again.');
            }
        } catch (err) {
            console.error(err);
            alert('Network error occurred.');
        } finally {
            certBtn.innerHTML = originalText;
            certBtn.disabled = false;
        }
    }

    // Payment Logic
    const paymentModal = document.getElementById('payment-modal');
    const closePaymentBtn = document.getElementById('close-payment');
    const payTossBtn = document.getElementById('pay-toss');
    const payPaypalBtn = document.getElementById('pay-paypal');
    const paypalContainer = document.getElementById('paypal-button-container');

    function openPaymentModal() {
        // Strict Login Requirement Check
        // If user profile element is missing, they are not logged in.
        const userProfile = document.querySelector('.user-profile');
        if (!userProfile) {
            alert("Login is required for payment and strict identity verification.\nRedirecting to login page...");
            window.location.href = "/auth/login"; // Adjust path if needed, usually /login or /auth/login
            return;
        }
        paymentModal.classList.remove('hidden');
    }

    closePaymentBtn.addEventListener('click', () => {
        paymentModal.classList.add('hidden');
        paypalContainer.classList.add('hidden');
        const sandboxMsg = document.getElementById('paypal-sandbox-msg');
        if (sandboxMsg) sandboxMsg.classList.add('hidden');

        // Reset Widget UI
        document.getElementById('payment-method').style.display = 'none';
        document.getElementById('toss-pay-submit').classList.add('hidden');

        paypalContainer.innerHTML = ''; // Clear PayPal buttons
        document.querySelector('.payment-options').style.display = 'flex';
    });

    // Toss Payments (Virtual / Demo Mode)
    // const clientKey = 'test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eqa'; // Test Key (Auth Error prevents usage)
    // const tossPayments = TossPayments(clientKey);

    // Unified Payment Success Handler
    function handlePaymentSuccess(providerName) {
        paymentModal.classList.add('hidden');

        // Create a temporary form to submit payment data first
        // In a real app, the provider calls a webhook. Here we simulate it.
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/api/mock-payment';
        form.style.display = 'none';

        const amountField = document.createElement('input');
        amountField.name = 'amount';
        amountField.value = '1000';
        form.appendChild(amountField);

        const nameField = document.createElement('input');
        nameField.name = 'payer_name';
        nameField.value = 'Hong Gil Dong'; // Simulation
        form.appendChild(nameField);

        const addrField = document.createElement('input');
        addrField.name = 'payer_address';
        addrField.value = 'Seoul, Korea (Bank Registered)';
        form.appendChild(addrField);

        document.body.appendChild(form);

        // After form submission and page reload (or redirect to success page)
        // The user should see the confirmation there.
        // Since form.submit() navigates away, we can't show alerts here easily 
        // unless we use fetch() instead. But mockup uses form submit to redirect.
        // Let's stick to the flow: Submit Form -> Server redirects to /payment-success -> 
        // /payment-success page shows the buttons/alerts requested.
        form.submit();
    }

    // Refund Logic
    const refundLink = document.getElementById('refund-link');
    if (refundLink) {
        refundLink.addEventListener('click', async () => {
            const reason = prompt("Enter refund reason:", "Accidental purchase");
            if (reason) {
                const transactionId = prompt("Enter Transaction ID (Simulated):", "TOSS_12345");
                if (transactionId) {
                    try {
                        const response = await fetch('/api/refund', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ transaction_id: transactionId, reason: reason })
                        });
                        const data = await response.json();
                        alert(data.message);
                    } catch (e) {
                        alert("Refund failed");
                    }
                }
            }
        });
    }

    // PayPal Smart Buttons
    let paypalButtonsRendered = false;
    payPaypalBtn.addEventListener('click', () => {
        document.querySelector('.payment-options').style.display = 'none';
        paypalContainer.classList.remove('hidden');
        document.getElementById('paypal-sandbox-msg').classList.remove('hidden');

        if (!paypalButtonsRendered) {
            paypal.Buttons({
                style: {
                    layout: 'vertical',
                    color: 'gold',
                    shape: 'rect',
                    label: 'paypal'
                },
                createOrder: function (data, actions) {
                    return actions.order.create({
                        purchase_units: [{
                            description: 'Toubina Premium Certificate',
                            amount: {
                                value: '3.50'
                            }
                        }]
                    });
                },
                onApprove: function (data, actions) {
                    return actions.order.capture().then(function (details) {
                        handlePaymentSuccess('PayPal');
                    });
                },
                onCancel: function (data) {
                    document.querySelector('.payment-options').style.display = 'flex';
                    paypalContainer.classList.add('hidden');
                },
                onError: function (err) {
                    console.error(err);
                    alert('PayPal Error occurred');
                    document.querySelector('.payment-options').style.display = 'flex';
                    paypalContainer.classList.add('hidden');
                }
            }).render('#paypal-button-container');
            paypalButtonsRendered = true;
        }
    });

    // --- Payment Logic with Localization ---

    // --- Payment Logic with Localization ---

    // --- Payment Logic with Localization ---

    // Initialize Toss Payments (Standard SDK)
    // Ref: https://docs.tosspayments.com/guides/v1/payment
    const clientKey = 'test_ck_D5GePWvyJnrK0W0k6q8gLzN97Eqa'; // Standard Test Key
    let tossPayments = null;
    try {
        tossPayments = TossPayments(clientKey);
    } catch (e) {
        console.error("Toss SDK Error:", e);
    }

    // Helper to get text based on current selection
    function getT(key) {
        const lang = document.getElementById('language-select').value || 'US';
        return (i18n[lang] || i18n['US'])[key];
    }

    // Toss Payments (Standard Redirection Window)
    payTossBtn.addEventListener('click', () => {
        if (!tossPayments) {
            alert("Payment System Initializing... Please refresh.");
            return;
        }

        // Save state before redirect
        // We can't easily persist the file, but we can persist the USER INTENT and maybe the result if we had it.
        // For now, at least the system will work.
        localStorage.setItem('payment_pending', 'true');

        // Directly request payment
        // This will open the Toss Payment Overlay/Redirect
        const orderId = 'ORDER_' + new Date().getTime();

        tossPayments.requestPayment('CARD', {
            amount: 3500,
            orderId: orderId,
            orderName: 'Toubina Premium Certificate',
            customerName: 'Customer',
            successUrl: window.location.origin + '/payment/success',
            failUrl: window.location.origin + '/payment/fail',
        }).catch(function (error) {
            if (error.code === 'USER_CANCEL') {
                // User cancelled
            } else {
                alert("Payment Error: " + error.message);
            }
        });
    });

    // Hidden handle for widget compatibility (Not used in this revert)
    const tossSubmitBtn = document.getElementById('toss-pay-submit');
    if (tossSubmitBtn) tossSubmitBtn.classList.add('hidden');
    document.getElementById('payment-method').style.display = 'none'; // Hide widget container

    resetBtn.addEventListener('click', () => {
        resultOverlay.classList.remove('active');
        resetUpload();
    });

    resetBtn.addEventListener('click', () => {
        resultOverlay.classList.remove('active');
        resetUpload();
    });

    // --- Launch Event Logic ---
    const shareModal = document.getElementById('share-modal');
    const fabBtn = document.getElementById('event-fab');
    const closeShareBtn = document.getElementById('close-share');

    if (fabBtn) {
        fabBtn.addEventListener('click', () => {
            shareModal.classList.remove('hidden');
        });
    }

    if (closeShareBtn) {
        closeShareBtn.addEventListener('click', () => {
            shareModal.classList.add('hidden');
        });
    }

    // --- Client-Side Translation Logic ---
    const langSelect = document.getElementById('language-select');
    const i18n = {
        'US': {
            'hero_title': 'Is this face <span class="gradient-text">Real?</span>',
            'hero_desc': 'Deepfake Detection, Authenticity Certificate (10 Free), Illegal Usage Tracking System',
            'tab_upload': 'Image/File<br>Upload',
            'tab_url': 'Video<br>Upload',
            'tab_marketing': 'Marketing<br>Tools',
            'upload_hint': 'Please upload an image here!',
            'upload_sub': 'Or drag and drop files.',
            'upload_info': 'Supports Images, PDF & Video',
            'url_placeholder': 'Paste YouTube, Instagram, TikTok Link...',
            'url_hint': 'Supported: YouTube, Instagram Reels, TikTok (Up to 10 min)',
            'marketing_title': 'YouTube Marketing Automation',
            'marketing_desc': 'Create a promotional video for Toubina and upload it directly to your channel.',
            'btn_analyze': 'Analyze Authenticity',
            'btn_certificate': 'Get Official Certificate',
            'btn_promo': 'Generate Promo Video',
            'btn_yt': 'Upload to YouTube',
            'btn_insta': 'Upload to Instagram Reels',
            'btn_tiktok': 'Upload to TikTok',
            'confidence_label': 'Manipulation Score',
            'new_scan': 'New Scan',
            'pay_title': 'Unlock Premium Certificate',
            'pay_desc': 'Get a verified digital certificate of this analysis.',
            'pay_confirm_toss': "Toubina Premium (aisolute.com)\n\nAmount: 3,500 KRW\nProceed with payment?",
            'pay_approve': "Approve payment?\n(Test Mode: OK = Success, Cancel = Fail)",
            'msg_checking': "Checking...",
            'tab_tracking': 'Tracking Detection<br>& Protection',
            'track_title': 'Illegal Usage Tracking',
            'track_desc': 'Monitor the web for unauthorized use of your content.',
            'feat_1_t': 'Auto Detection',
            'feat_1_d': 'SNS, Mall, Blog, Community',
            'feat_2_t': 'Real-time Alerts',
            'feat_2_d': 'Instant notification',
            'feat_3_t': 'Auto Response',
            'feat_3_d': 'Auto countermeasures',
            'feat_4_t': 'Warning Emails',
            'feat_4_d': 'Auto-send custom warnings',
            'feat_5_t': 'Takedown Request',
            'feat_5_d': 'Auto broadcast deletion',
            'btn_track_start': 'Activate Protection'
        },
        'KR': {
            'hero_title': '이 얼굴, <span class="gradient-text">진짜일까?</span>',
            'hero_desc': '딥페이크 탐지, 진위 인증서 발급(10회 무료), 불법 사용 추적 시스템',
            'tab_upload': '이미지/파일<br>업로드',
            'tab_url': '동영상<br>업로드',
            'tab_marketing': '마케팅<br>도구',
            'upload_hint': '여기에 이미지를 업로드 해주세요!',
            'upload_sub': '또는 파일을 드래그 해주세요.',
            'upload_info': '지원: 이미지, PDF, 동영상',
            'url_placeholder': '유튜브, 인스타그램, 틱톡 링크 붙여넣기...',
            'url_hint': '지원: 유튜브, 인스타그램 릴스, 틱톡 (최대 10분)',
            'marketing_title': '유튜브 마케팅 자동화',
            'marketing_desc': 'Toubina 홍보 영상을 생성하여 채널에 바로 업로드하세요.',
            'btn_analyze': '진위 여부 분석하기',
            'btn_certificate': '공식 인증서 발급받기',
            'btn_promo': '홍보 영상 생성하기',
            'btn_yt': '유튜브에 업로드',
            'btn_insta': '인스타그램 릴스에 업로드',
            'btn_tiktok': '틱톡에 업로드',
            'confidence_label': '조작 의심률',
            'new_scan': '새로운 분석',
            'pay_title': '프리미엄 인증서 잠금 해제',
            'pay_desc': '이 분석에 대한 검증된 디지털 인증서를 발급받으세요.',
            'pay_confirm_toss': "Toubina Premium (aisolute.com)\n\n결제 금액: 3,500원\n결제를 진행하시겠습니까?",
            'pay_approve': "결제를 승인하시겠습니까?\n(테스트 모드: 확인 = 성공, 취소 = 실패)",
            'msg_checking': "확인 중...",
            'tab_tracking': '추적 탐지<br>및 보호',
            'track_title': '불법 사용 추적 시스템',
            'track_desc': '웹상의 무단 콘텐츠 사용을 실시간으로 감시합니다.',
            'feat_1_t': '자동 탐지',
            'feat_1_d': 'SNS, 쇼핑몰, 블로그, 커뮤니티',
            'feat_2_t': '실시간 알림',
            'feat_2_d': '불법 사용 발견 시 즉시 알림',
            'feat_3_t': '자동 대응 시스템',
            'feat_3_d': '대응 조치 자동화',
            'feat_4_t': '경고 메일 발송',
            'feat_4_d': '자동 경고 메일 발송',
            'feat_5_t': '삭제 요청 방송',
            'feat_5_d': '삭제 요청 자동 방송',
            'btn_track_start': '보호 활성화'
        },
    };

    function updateLanguage(lang) {
        const t = i18n[lang] || i18n['US'];

        // Crucial for Browser Detection (Edge, Chrome)
        document.documentElement.lang = (lang === 'KR' ? 'ko' : 'en');

        // Hero
        document.querySelector('.hero h1').innerHTML = t.hero_title;
        document.querySelector('.hero p').innerText = t.hero_desc;

        // Tabs
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[0]) tabs[0].innerHTML = t.tab_upload;
        if (tabs[1]) tabs[1].innerHTML = t.tab_url;
        if (tabs[2]) tabs[2].innerHTML = t.tab_tracking;
        if (tabs[3]) tabs[3].innerHTML = t.tab_marketing;

        // Upload
        const uploadBox = document.querySelector('.upload-content h3');
        if (uploadBox) uploadBox.innerText = t.upload_hint;
        const uploadSub = document.querySelector('.upload-content p');
        if (uploadSub) uploadSub.innerText = t.upload_sub;
        const uploadInfo = document.querySelector('.file-info');
        if (uploadInfo) uploadInfo.innerText = t.upload_info;

        // URL
        const urlIn = document.getElementById('youtube-url');
        if (urlIn) urlIn.placeholder = t.url_placeholder;
        const urlHint = document.querySelector('.url-hint');
        if (urlHint && t.url_hint) urlHint.textContent = t.url_hint;

        // Marketing
        const mktTitle = document.querySelector('.marketing-card h3');
        if (mktTitle) mktTitle.innerText = t.marketing_title;
        const mktDesc = document.querySelector('.marketing-card p');
        if (mktDesc) mktDesc.innerText = t.marketing_desc;
        const promoBtn = document.getElementById('create-promo-btn');
        if (promoBtn) promoBtn.innerHTML = `<i class="fa-solid fa-video"></i> ${t.btn_promo}`;

        // Social Upload Buttons
        const ytBtn = document.getElementById('upload-yt-btn');
        if (ytBtn && t.btn_yt) ytBtn.innerHTML = `<i class="fa-brands fa-youtube"></i> ${t.btn_yt}`;
        const instaBtn = document.getElementById('upload-insta-btn');
        if (instaBtn && t.btn_insta) instaBtn.innerHTML = `<i class="fa-brands fa-instagram"></i> ${t.btn_insta}`;
        const tiktokBtn = document.getElementById('upload-tiktok-btn');
        if (tiktokBtn && t.btn_tiktok) tiktokBtn.innerHTML = `<i class="fa-brands fa-tiktok" style="color: #00f2ea;"></i> <span style="margin-left:5px; color: #ff0050;">${t.btn_tiktok}</span>`;

        // Tracking
        const trkTitle = document.getElementById('track-title');
        if (trkTitle) trkTitle.innerText = t.track_title;
        const trkDesc = document.getElementById('track-desc');
        if (trkDesc) trkDesc.innerText = t.track_desc;
        const btnTrack = document.querySelector('.btn-track-start');
        if (btnTrack) btnTrack.innerText = t.btn_track_start;

        for (let i = 1; i <= 5; i++) {
            const ft = document.querySelector('.feat-title-' + i);
            if (ft) ft.innerText = t['feat_' + i + '_t'];
            const fd = document.querySelector('.feat-desc-' + i);
            if (fd) fd.innerText = t['feat_' + i + '_d'];
        }

        // Buttons
        const anaBtn = document.querySelector('#analyze-btn .btn-text');
        if (anaBtn) anaBtn.innerText = t.btn_analyze;

        // Certificate Button (Dynamic)
        const certBtn = document.getElementById('cert-btn');
        if (certBtn) certBtn.innerHTML = `<i class="fa-solid fa-certificate"></i> ${t.btn_certificate}`;

        // Result Area
        const confLabel = document.querySelector('.meter-label');
        if (confLabel && t.confidence_label) confLabel.innerText = t.confidence_label;
        const resetBtn = document.getElementById('reset-btn');
        if (resetBtn && t.new_scan) resetBtn.innerText = t.new_scan;

        // Payment Modal
        const payTitle = document.querySelector('.payment-card h3');
        if (payTitle) payTitle.innerText = t.pay_title;
        const payDesc = document.querySelector('.payment-card p');
        if (payDesc) payDesc.innerText = t.pay_desc;

        // FORCE CORRECT PRICING DISPLAY
        // To ensure user always sees the correct updated price
        const tossPrice = document.querySelector('#pay-toss .pay-info span');
        if (tossPrice) tossPrice.textContent = '3,500 KRW';

        const paypalPrice = document.querySelector('#pay-paypal .pay-info span');
        if (paypalPrice) paypalPrice.textContent = '$3.50 USD';
    }

    if (langSelect) {
        langSelect.addEventListener('change', (e) => {
            console.log('Language changed to:', e.target.value);
            updateLanguage(e.target.value);
        });

        // Initialize based on current selection
        // Determine browser language if not set? 
        // For now, respect the select box default (which is US in HTML).
        console.log('Initial language:', langSelect.value);
        updateLanguage(langSelect.value);
    }
});