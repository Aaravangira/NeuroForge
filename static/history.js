async function loadHistory(){

    try{

        const response = await fetch("/history");

        const data = await response.json();

        const tbody =
            document.getElementById("historyTable");

        tbody.innerHTML="";

        if(data.data.length===0){

            tbody.innerHTML=`

            <tr>

                <td colspan="7"
                    class="text-center">

                    No invoices found.

                </td>

            </tr>

            `;

            return;

        }

        data.data.forEach(invoice=>{

            tbody.innerHTML+=`

            <tr>

                <td>${invoice.id}</td>

                <td>${invoice.vendor_name||"-"}</td>

                <td>${invoice.invoice_number||"-"}</td>

                <td>${invoice.invoice_date||"-"}</td>

                <td>₹${invoice.grand_total||0}</td>

                <td>

                    <span class="status status-success">

                        Processed

                    </span>

                </td>

                <td>

                    <button
                        class="btn btn-sm btn-primary">

                        View

                    </button>

                </td>

            </tr>

            `;

        });

    }

    catch(e){

        console.log(e);

    }

}

document
.addEventListener(
    "DOMContentLoaded",
    loadHistory
);