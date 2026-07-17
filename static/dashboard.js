// ======================================
// Dashboard Loader
// ======================================

async function loadDashboard(){

    try{

        const response = await fetch("/dashboard");

        const data = await response.json();

        if(!data.success){

            return;

        }

        document.getElementById("invoiceCount").innerHTML =
            data.total_invoices;

        document.getElementById("totalAmount").innerHTML =
            "₹" + Number(data.total_amount).toLocaleString();

        loadRecentInvoices(data.data);

    }

    catch(error){

        console.log(error);

    }

}

// ======================================
// Recent Invoice Table
// ======================================

function loadRecentInvoices(invoices){

    const tbody =
        document.getElementById("recentInvoices");

    if(!tbody){

        return;

    }

    tbody.innerHTML="";

    if(invoices.length===0){

        tbody.innerHTML=`

        <tr>

            <td colspan="5"
                class="text-center">

                No invoices found.

            </td>

        </tr>

        `;

        return;

    }

    invoices.slice(0,5).forEach(invoice=>{

        tbody.innerHTML+=`

        <tr>

            <td>

                ${invoice.vendor_name||"-"}

            </td>

            <td>

                ${invoice.invoice_number||"-"}

            </td>

            <td>

                ${invoice.invoice_date||"-"}

            </td>

            <td>

                ₹${invoice.grand_total||0}

            </td>

            <td>

                <span class="status status-success">

                    Processed

                </span>

            </td>

        </tr>

        `;

    });

}

document.addEventListener(

    "DOMContentLoaded",

    loadDashboard

);