"use strict";

/* ==========================================================
   AI INVOICE EXTRACTOR
   Invoice Upload UI
   ========================================================== */

const form = document.getElementById("uploadForm");
const loading = document.getElementById("loading");
const result = document.getElementById("result");


// ==========================================================
// HELPERS
// ==========================================================

function setLoading(visible) {
    if (loading) {
        loading.style.display = visible ? "block" : "none";
    }
}


function showError(message) {
    if (!result) {
        return;
    }

    result.innerHTML = `
        <div class="alert alert-danger">
            ${escapeHtml(message)}
        </div>
    `;
}


function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ==========================================================
// UPLOAD
// ==========================================================

if (form) {

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const fileInput =
                document.getElementById("file");

            if (
                !fileInput ||
                fileInput.files.length === 0
            ) {

                showError(
                    "Please select a document."
                );

                return;
            }

            const file =
                fileInput.files[0];

            const formData =
                new FormData();

            formData.append(
                "file",
                file
            );

            setLoading(true);

            if (result) {
                result.innerHTML = "";
            }

            try {

                const response =
                    await fetch(
                        "/upload/",
                        {
                            method: "POST",
                            body: formData
                        }
                    );

                let data = null;

                try {
                    data = await response.json();
                } catch {
                    throw new Error(
                        "Server returned an invalid response."
                    );
                }

                if (
                    !response.ok ||
                    !data ||
                    !data.success
                ) {

                    throw new Error(
                        data?.detail ||
                        data?.message ||
                        "Invoice upload failed."
                    );
                }

                /*
                 * Backend currently returns:
                 *
                 * {
                 *   success: true,
                 *   invoice: {...},
                 *   excel_file: "..."
                 * }
                 *
                 * Support `document` temporarily as a
                 * backward-compatible fallback.
                 */

                const document =
                    data.invoice ||
                    data.document;

                if (!document) {

                    throw new Error(
                        "Invoice data was not returned by the server."
                    );
                }

                renderInvoice(
                    document,
                    data.excel_file
                );

            } catch (error) {

                console.error(
                    "Invoice upload error:",
                    error
                );

                showError(
                    error?.message ||
                    "Invoice upload failed."
                );

            } finally {

                setLoading(false);
            }
        }
    );
}


// ==========================================================
// RENDER INVOICE
// ==========================================================

function renderInvoice(
    document,
    excelFile
) {

    if (!result) {
        return;
    }

    let html = `

        <div class="card shadow-lg invoice-card">

            <div class="invoice-header">

                <h3>📄 Document Information</h3>

            </div>

            <div class="invoice-body">

                <table class="table table-bordered">

                    <tr>
                        <th>Document Type</th>
                        <td>
                            ${escapeHtml(
                                document.document_type
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Document Number</th>
                        <td>
                            ${escapeHtml(
                                document.document_number ||
                                document.invoice_number
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Document Date</th>
                        <td>
                            ${escapeHtml(
                                document.document_date ||
                                document.invoice_date
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Currency</th>
                        <td>
                            ${escapeHtml(
                                document.currency
                            )}
                        </td>
                    </tr>

                </table>

                <hr>

                <h4>🏢 Vendor</h4>

                <table class="table table-bordered">

                    <tr>
                        <th>Name</th>
                        <td>
                            ${escapeHtml(
                                document.vendor?.name ||
                                document.vendor_name
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>GST</th>
                        <td>
                            ${escapeHtml(
                                document.vendor?.gst ||
                                document.gst_number
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>PAN</th>
                        <td>
                            ${escapeHtml(
                                document.vendor?.pan
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Phone</th>
                        <td>
                            ${escapeHtml(
                                document.vendor?.phone
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Email</th>
                        <td>
                            ${escapeHtml(
                                document.vendor?.email
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Address</th>
                        <td>
                            ${escapeHtml(
                                document.vendor?.address
                            )}
                        </td>
                    </tr>

                </table>

                <hr>

                <h4>👤 Buyer</h4>

                <table class="table table-bordered">

                    <tr>
                        <th>Name</th>
                        <td>
                            ${escapeHtml(
                                document.buyer?.name ||
                                document.buyer_name
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>GST</th>
                        <td>
                            ${escapeHtml(
                                document.buyer?.gst
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Phone</th>
                        <td>
                            ${escapeHtml(
                                document.buyer?.phone
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Email</th>
                        <td>
                            ${escapeHtml(
                                document.buyer?.email
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Address</th>
                        <td>
                            ${escapeHtml(
                                document.buyer?.address
                            )}
                        </td>
                    </tr>

                </table>

                <hr>

                <h4>💰 Amount Details</h4>

                <table class="table table-bordered">

                    <tr>
                        <th>Subtotal</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.subtotal ||
                                document.subtotal
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Discount</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.discount ||
                                document.discount
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>CGST</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.cgst ||
                                document.cgst
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>SGST</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.sgst ||
                                document.sgst
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>IGST</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.igst ||
                                document.igst
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>VAT</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.vat ||
                                document.vat
                            )}
                        </td>
                    </tr>

                    <tr>
                        <th>Grand Total</th>
                        <td>
                            <strong>
                                ${escapeHtml(
                                    document.amounts?.grand_total ||
                                    document.grand_total
                                )}
                            </strong>
                        </td>
                    </tr>

                    <tr>
                        <th>Amount Paid</th>
                        <td>
                            ${escapeHtml(
                                document.amounts?.amount_paid
                            )}
                        </td>
                    </tr>

                </table>

                <hr>

                <h4>📦 Items</h4>

                <table class="table table-striped table-bordered">

                    <thead>

                        <tr>
                            <th>Description</th>
                            <th>Qty</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>

                    </thead>

                    <tbody>
    `;

    if (
        Array.isArray(document.items) &&
        document.items.length > 0
    ) {

        document.items.forEach(
            function (item) {

                html += `

                    <tr>

                        <td>
                            ${escapeHtml(
                                item.description ||
                                item.title
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                item.quantity
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                item.unit_price
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                item.total
                            )}
                        </td>

                    </tr>
                `;
            }
        );

    } else {

        html += `
            <tr>
                <td colspan="4" class="text-center">
                    No line items found.
                </td>
            </tr>
        `;
    }

    html += `

                    </tbody>

                </table>

            </div>

        </div>

    `;

    if (excelFile) {

        const downloadUrl =
            "/download-excel";

        html += `

            <div class="mt-3">

                <a
                    href="${downloadUrl}"
                    class="btn btn-success"
                >
                    📥 Download Excel
                </a>

            </div>

        `;
    }

    result.innerHTML = html;
}