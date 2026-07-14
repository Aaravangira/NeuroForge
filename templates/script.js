const form = document.getElementById("uploadForm");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const fileInput = document.getElementById("file");

    if (fileInput.files.length === 0) {
        alert("Please select a PDF.");
        return;
    }

    document.getElementById("loading").style.display = "block";
    document.getElementById("result").innerHTML = "";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        document.getElementById("loading").style.display = "none";

        if (!data.success) {
            document.getElementById("result").innerHTML =
                `<div class="alert alert-danger">${data.message}</div>`;
            return;
        }

        const invoice = data.invoice;

        let html = `

        <div class="card shadow mt-4">

            <div class="card-header bg-success text-white">
                <h4>Invoice Details</h4>
            </div>

            <div class="card-body">

                <table class="table table-bordered">

                    <tr>
                        <th>Invoice Number</th>
                        <td>${invoice.invoice_number ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Invoice Date</th>
                        <td>${invoice.invoice_date ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Vendor</th>
                        <td>${invoice.vendor?.name ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Buyer</th>
                        <td>${invoice.buyer?.name ?? ""}</td>
                    </tr>

                    <tr>
                        <th>GST Number</th>
                        <td>${invoice.vendor?.gst ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Grand Total</th>
                        <td>₹ ${invoice.amounts?.grand_total ?? ""}</td>
                    </tr>

                </table>

                <h4 class="mt-4">Items</h4>

                <table class="table table-striped">

                    <thead>

                        <tr>
                            <th>Description</th>
                            <th>Qty</th>
                            <th>Total</th>
                        </tr>

                    </thead>

                    <tbody>
        `;

        if (invoice.items && invoice.items.length > 0) {

            invoice.items.forEach(item => {

                html += `
                    <tr>
                        <td>${item.title || item.description || ""}</td>
                        <td>${item.quantity || ""}</td>
                        <td>${item.total || ""}</td>
                    </tr>
                `;
            });

        }

        html += `
                    </tbody>

                </table>

            </div>

        </div>
        `;

        document.getElementById("result").innerHTML = html;

    } catch (err) {

        document.getElementById("loading").style.display = "none";

        document.getElementById("result").innerHTML =
            `<div class="alert alert-danger">${err}</div>`;
    }

});