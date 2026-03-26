"use strict"

const refresh_btns = document.querySelectorAll('.refresh-connection');
const delete_btns = document.querySelectorAll('.remove-connection')

if (refresh_btns.length) {
    refresh_btns.forEach(btn => {
        btn.addEventListener('click', async (event) => {
            const node_url = btn.dataset.nodeUrl;
            const local_url = btn.dataset.localUrl;

            try {
                const url = `${local_url}/api/nodes/${encodeURIComponent(node_url)}`
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrftoken,
                    }
                });

                if (!response.ok) {
                    console.error('Refresh failed:', response.status);
                }
        
            } catch(error) {
                console.log(error);
            }
        });
    })
}

if (delete_btns.length) {
    delete_btns.forEach(btn => {
        btn.addEventListener('click', async (event) => {
            const node_url = btn.dataset.nodeUrl;
            const local_url = btn.dataset.localUrl;

            try {
                const url = `${local_url}/api/nodes/${encodeURIComponent(node_url)}`
                const response = await fetch(url, {
                    method: "DELETE",
                    headers: {
                        'X-CSRFToken': csrftoken,
                    }
                });

                if (!response.ok) {
                    console.error('Refresh failed:', response.status);
                }
        
            } catch(error) {
                console.log(error);
            }
        });
    })
}
