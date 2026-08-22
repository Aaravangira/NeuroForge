// ==========================================================
// INVOICE HISTORY
// ==========================================================

async function loadHistory() {

    try {

        const response = await fetch("/history");

        if (!response.ok) {
            throw new Error(
                `History request failed: ${response.status}`
            );
        }

        const data = await response.json();

        const tbody =
            document.getElementById("historyTable");

        if (!tbody) {
            console.error(
                "historyTable element not found."
            );
            return;
        }

        tbody.innerHTML = "";

        // --------------------------------------------------
        // EMPTY HISTORY
        // --------------------------------------------------

        if (
            !data.success ||
            !Array.isArray(data.data) ||
            data.data.length === 0
        ) {

            tbody.innerHTML = `
                <tr>
                    <td
                        colspan="7"
                        class="text-center"
                    >
                        No invoices found.
                    </td>
                </tr>
            `;

            return;
        }

        // --------------------------------------------------
        // RENDER HISTORY
        // --------------------------------------------------

        data.data.forEach(
            (invoice) => {

                const invoiceId =
                    Number(invoice.id);

                tbody.innerHTML += `
                    <tr>

                        <td>
                            ${invoiceId}
                        </td>

                        <td>
                            ${escapeHtml(
                                invoice.vendor_name || "-"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                invoice.invoice_number || "-"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                invoice.invoice_date || "-"
                            )}
                        </td>

                        <td>
                            ₹${escapeHtml(
                                invoice.grand_total || "0"
                            )}
                        </td>

                        <td>

                            <span
                                class="status status-success"
                            >
                                Processed
                            </span>

                        </td>

                        <td>

                            <div
                                class="action-buttons"
                            >

                                <button
                                    type="button"
                                    class="btn btn-sm btn-primary"
                                    onclick="viewInvoice(${invoiceId})"
                                >
                                    <i class="bi bi-eye"></i>
                                    View
                                </button>

                                <button
                                    type="button"
                                    class="btn btn-sm btn-danger"
                                    onclick="deleteInvoice(${invoiceId})"
                                >
                                    <i class="bi bi-trash"></i>
                                    Delete
                                </button>

                            </div>

                        </td>

                    </tr>
                `;
            }
        );

    }

    catch (error) {

        console.error(
            "History loading error:",
            error
        );

        const tbody =
            document.getElementById(
                "historyTable"
            );

        if (tbody) {

            tbody.innerHTML = `
                <tr>
                    <td
                        colspan="7"
                        class="text-center text-danger"
                    >
                        Failed to load invoice history.
                    </td>
                </tr>
            `;
        }
    }
}


// ==========================================================
// VIEW INVOICE
// ==========================================================

function viewInvoice(
    invoiceId
) {

    if (!invoiceId) {
        return;
    }

    window.location.href =
        `/invoices/${invoiceId}`;
}


// ==========================================================
// DELETE INVOICE
// ==========================================================

async function deleteInvoice(
    invoiceId
) {

    if (!invoiceId) {

        alert(
            "Invalid invoice ID."
        );

        return;
    }

    // ------------------------------------------------------
    // CONFIRMATION
    // ------------------------------------------------------

    const confirmed =
        window.confirm(
            `Are you sure you want to delete invoice #${invoiceId}?`
        );

    if (!confirmed) {
        return;
    }

    try {

        const response =
            await fetch(
                `/invoices/${invoiceId}`,
                {
                    method: "DELETE",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

        const data =
            await response.json();

        // --------------------------------------------------
        // API ERROR
        // --------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Failed to delete invoice."
            );
        }

        // --------------------------------------------------
        // SUCCESS
        // --------------------------------------------------

        if (data.success) {

            alert(
                "Invoice deleted successfully."
            );

            await loadHistory();

            // Refresh dashboard counters if present
            refreshDashboard();
        }

    }

    catch (error) {

        console.error(
            "Delete invoice error:",
            error
        );

        alert(
            error.message ||
            "Failed to delete invoice."
        );
    }
}


// ==========================================================
// REFRESH DASHBOARD
// ==========================================================

async function refreshDashboard() {

    try {

        const response =
            await fetch(
                "/api/dashboard"
            );

        if (!response.ok) {
            return;
        }

        const result =
            await response.json();

        if (
            !result.success ||
            !result.data
        ) {
            return;
        }

        const totalInvoices =
            document.getElementById(
                "totalInvoices"
            );

        const totalAmount =
            document.getElementById(
                "totalAmount"
            );

        if (totalInvoices) {

            totalInvoices.textContent =
                result.data.total_invoices;
        }

        if (totalAmount) {

            totalAmount.textContent =
                result.data.total_amount;
        }

    }

    catch (error) {

        console.warn(
            "Dashboard refresh failed:",
            error
        );
    }
}


// ==========================================================
// HTML ESCAPE
// ==========================================================

function escapeHtml(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


// ==========================================================
// INITIALIZE
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {
        loadHistory();
    }
);