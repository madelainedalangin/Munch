"use static"

async function initializeFollowBtnState(btn_follow) {
    try {
        const author_fqid = btn_follow.dataset.authorFqid;
        const user_fqid = btn_follow.dataset.userFqid;

        const response = await fetch(`${user_fqid}/following/${author_fqid}`);

        if (response.status === 200) {
            btn_follow.classList.toggle('following');
            btn_follow.textContent = 'Unfollow';
        }

    } catch(error) {
        console.log(error);
    }
}

async function manageAuthorFollow(btn_follow, user_fqid, author_fqid, http_method) {
    try {
        const url = `${user_fqid}/following/${author_fqid}`
        const response = await fetch(url, {
            method: http_method,
            headers: {
                'X-CSRFToken': csrftoken,
            }
        });

    } catch(error) {
        console.log(error);
        btn_follow.classList.toggle('following'); // undo toggle
    }
}

const btn_follow = document.querySelector('#follow');

if (btn_follow) {
    initializeFollowBtnState(btn_follow);
    btn_follow.addEventListener('click', (event) => {
        const author_fqid = btn_follow.dataset.authorFqid;
        const user_fqid = btn_follow.dataset.userFqid;
        const isFollowing = btn_follow.classList.toggle('following');   // returns new state

        if (isFollowing) {
            btn_follow.textContent = 'Unfollow';
            manageAuthorFollow(btn_follow, user_fqid, author_fqid, 'PUT');

        } else {
            btn_follow.textContent = 'Follow';
            manageAuthorFollow(btn_follow, user_fqid, author_fqid, 'DELETE');
        }
    });
}

