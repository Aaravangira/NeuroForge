document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("invoiceFile");
    const dropzone = document.getElementById("invoiceDropzone");
    const selectedFile = document.getElementById("selectedFile");
    const fileName = document.getElementById("selectedFileName");
    const fileSize = document.getElementById("selectedFileSize");
    const removeButton = document.getElementById("removeSelectedFile");
    const processButton = document.getElementById("processInvoice");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    // --------------------------------------------------
    // Make sure this script only runs on the upload page
    // --------------------------------------------------

    if (!fileInput || !processButton) {
        return;
    }

    let selectedInvoiceFile = null;

    // --------------------------------------------------
    // Utility: escape HTML
    // --------------------------------------------------

    function escapeHtml(value) {
        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // --------------------------------------------------
    // Format file size
    // --------------------------------------------------

    function formatFileSize(bytes) {

        if (!bytes) {
            return "0 KB";
        }

        const kb = bytes / 1024;

        if (kb < 1024) {
            return kb.toFixed(1) + " KB";
        }

        return (kb / 1024).toFixed(2) + " MB";
    }

    // --------------------------------------------------
    // Show selected file
    // --------------------------------------------------

    function showFile(file) {

        if (!file) {
            return;
        }

        const allowedTypes = [
            "application/pdf",
            "image/png",
            "image/jpeg"
        ];

        const allowedExtensions = [
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg"
        ];

        const extension = "." + file.name.split(".").pop().toLowerCase();

        if (
            !allowedTypes.includes(file.type) &&
            !allowedExtensions.includes(extension)
        ) {
            alert("Please select a PDF, PNG, JPG, or JPEG invoice.");
            fileInput.value = "";
            return;
        }

        selectedInvoiceFile = file;

        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);

        selectedFile.style.display = "flex";
        processButton.disabled = false;

        dropzone.classList.add("has-file");

        result.innerHTML = "";
    }

    // --------------------------------------------------
    // File input
    // --------------------------------------------------

    fileInput.addEventListener("change", function () {

        if (this.files && this.files.length > 0) {
            showFile(this.files[0]);
        }

    });

    // --------------------------------------------------
    // Remove selected file
    // --------------------------------------------------

    removeButton.addEventListener("click", function () {

        selectedInvoiceFile = null;

        fileInput.value = "";

        selectedFile.style.display = "none";

        processButton.disabled = true;

        dropzone.classList.remove("has-file");

        result.innerHTML = "";

    });

    // --------------------------------------------------
    // Drag & Drop
    // --------------------------------------------------

    ["dragenter", "dragover"].forEach(function (eventName) {

        dropzone.addEventListener(eventName, function (event) {

            event.preventDefault();
            event.stopPropagation();

            dropzone.classList.add("drag-active");

        });

    });

    ["dragleave", "drop"].forEach(function (eventName) {

        dropzone.addEventListener(eventName, function (event) {

            event.preventDefault();
            event.stopPropagation();

            dropzone.classList.remove("drag-active");

        });

    });

    dropzone.addEventListener("drop", function (event) {

        const files = event.dataTransfer.files;

        if (!files || files.length === 0) {
            return;
        }

        try {
            fileInput.files = files;
        } catch (error) {
            console.warn("Could not assign dropped files:", error);
        }

        showFile(files[0]);

    });

    // --------------------------------------------------
    // Render extraction result
    // --------------------------------------------------

    function renderResult(invoice, excelFile) {

        const vendorName =
            invoice.vendor_name ||
            invoice.vendor ||
            invoice.supplier_name ||
            "-";

        const invoiceNumber =
            invoice.invoice_number ||
            invoice.document_number ||
            "-";

        const invoiceDate =
            invoice.invoice_date ||
            invoice.document_date ||
            "-";

        const grandTotal =
            invoice.grand_total ??
            invoice.total ??
            invoice.total_amount ??
            "-";

        const currency =
            invoice.currency ||
            "INR";

        const paymentMethod =
            invoice.payment_method ||
            "-";

        const invoiceId =
            invoice.invoice_id ||
            invoice.id ||
            "-";

        let downloadUrl = null;

        if (excelFile) {
            downloadUrl = "/download/excel";
        }

        result.innerHTML = `
            <div class="extraction-result">

                <div class="result-header">
                    <div>
                        <span class="section-kicker">EXTRACTION COMPLETE</span>
                        <h3>Invoice processed successfully</h3>
                        <p>
                            AI extraction completed and the invoice has been
                            saved to your workspace.
                        </p>
                    </div>

                    <div class="result-success-icon">
                        <i class="bi bi-check-lg"></i>
                    </div>
                </div>

                <div class="result-grid">

                    <div class="result-field">
                        <span>Vendor</span>
                        <strong>${escapeHtml(vendorName)}</strong>
                    </div>

                    <div class="result-field">
                        <span>Invoice number</span>
                        <strong>${escapeHtml(invoiceNumber)}</strong>
                    </div>

                    <div class="result-field">
                        <span>Invoice date</span>
                        <strong>${escapeHtml(invoiceDate)}</strong>
                    </div>

                    <div class="result-field result-total">
                        <span>Grand total</span>
                        <strong>
                            ${escapeHtml(currency)}
                            ${escapeHtml(grandTotal)}
                        </strong>
                    </div>

                    <div class="result-field">
                        <span>Payment method</span>
                        <strong>${escapeHtml(paymentMethod)}</strong>
                    </div>

                    <div class="result-field">
                        <span>Invoice ID</span>
                        <strong>#${escapeHtml(invoiceId)}</strong>
                    </div>

                </div>

                <div class="result-actions">

                    ${
                        downloadUrl
                            ? `
                                <a
                                    href="${downloadUrl}"
                                    class="primary-action"
                                    download
                                >
                                    <i class="bi bi-file-earmark-spreadsheet"></i>
                                    Download Excel
                                </a>
                            `
                            : ""
                    }

                    <a
                        href="/history-page"
                        class="secondary-action"
                    >
                        <i class="bi bi-receipt"></i>
                        View invoices
                    </a>

                    <button
                        type="button"
                        class="secondary-action"
                        id="processAnother"
                    >
                        <i class="bi bi-plus-lg"></i>
                        Process another
                    </button>

                </div>

            </div>
        `;

        const processAnother =
            document.getElementById("processAnother");

        if (processAnother) {

            processAnother.addEventListener("click", function () {

                selectedInvoiceFile = null;

                fileInput.value = "";

                selectedFile.style.display = "none";

                processButton.disabled = true;

                dropzone.classList.remove("has-file");

                result.innerHTML = "";

                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });

            });

        }
    }

    // --------------------------------------------------
    // Render error
    // --------------------------------------------------

    function renderError(message) {

        result.innerHTML = `
            <div class="extraction-error">

                <div class="error-icon">
                    <i class="bi bi-exclamation-triangle"></i>
                </div>

                <div>
                    <strong>Invoice processing failed</strong>
                    <p>${escapeHtml(message)}</p>
                </div>

            </div>
        `;

    }

    // --------------------------------------------------
    // Process Invoice
    // --------------------------------------------------

    processButton.addEventListener("click", async function () {

        if (!selectedInvoiceFile) {

            alert("Please select an invoice first.");

            return;
        }

        const formData = new FormData();

        formData.append("file", selectedInvoiceFile);

        // Disable UI during processing
        processButton.disabled = true;

        selectedFile.style.display = "none";

        loading.style.display = "flex";

        result.innerHTML = "";

        dropzone.classList.add("processing");

        try {

            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            let data;

            try {
                data = await response.json();
            } catch (jsonError) {
                throw new Error(
                    "The server returned an invalid response."
                );
            }

            if (!response.ok || !data.success) {

                throw new Error(
                    data.message ||
                    data.detail ||
                    "Invoice processing failed."
                );

            }

            const invoice =
                data.invoice ||
                data.document;

            if (!invoice) {

                throw new Error(
                    "Invoice processed successfully, but no extracted data was returned."
                );

            }

            renderResult(
                invoice,
                data.excel_file
            );

        } catch (error) {

            console.error(
                "Invoice processing error:",
                error
            );

            renderError(
                error.message ||
                "Unable to process the invoice. Please try again."
            );

        } finally {

            loading.style.display = "none";

            dropzone.classList.remove("processing");

            processButton.disabled =
                !selectedInvoiceFile;

            if (selectedInvoiceFile) {
                selectedFile.style.display = "flex";
            }

        }

    });

});