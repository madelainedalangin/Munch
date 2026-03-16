"use strict"

const csrftoken = document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

async function initializeFollowButtonState(follow_button) {
    try {
        const author_uuid = follow_button.dataset.authorUuid;
        const user_uuid = follow_button.dataset.userUuid;

        // check accepted follows
        const response = await fetch(`/munch/api/authors/${user_uuid}/following/${author_uuid}/`);

        if (response.status === 200) {
            const data = await response.json();
            console.log('data', JSON.stringify(data));
            if (data.status === 'accepted') {
                follow_button.classList.add('following');
                follow_button.textContent = 'Following';
                follow_button.dataset.state = 'accepted';
            } else if (data.status === 'requesting') {
                follow_button.classList.add('requesting');
                follow_button.textContent = 'Friend Request Sent';
                follow_button.dataset.state = 'requesting';
            }
        } else {
            follow_button.textContent = 'Follow';
            follow_button.dataset.state = 'none';
        }

    } catch (error) {
        console.log(error);
    }
}

async function manageAuthorFollow(follow_button, user_uuid, author_uuid, http_method) {
    try {
        const url = `/munch/api/authors/${user_uuid}/following/${author_uuid}/`;
        console.log('manageAuthorFollow URL:', url);
        const response = await fetch(url, {
            method: http_method,
            headers: {
                'X-CSRFToken': csrftoken,
            }
        });
    } catch (error) {
        console.log(error);
    }
}

const follow_button = document.querySelector('#follow');

if (follow_button) {
    initializeFollowButtonState(follow_button);
    follow_button.addEventListener('click', (event) => {
        console.log('Follow button clicked!');
        console.log('state:', follow_button.dataset.state);

        const author_uuid = follow_button.dataset.authorUuid;
        const user_uuid = follow_button.dataset.userUuid;
        const state = follow_button.dataset.state;

        if (state === 'none') {
            follow_button.textContent = 'Friend Request Sent';
            follow_button.dataset.state = 'requesting';
            follow_button.classList.add('requesting');
            manageAuthorFollow(follow_button, user_uuid, author_uuid, 'PUT');

        } else if (state === 'requesting') {
            follow_button.textContent = 'Follow';
            follow_button.dataset.state = 'none';
            follow_button.classList.remove('requesting');
            manageAuthorFollow(follow_button, user_uuid, author_uuid, 'DELETE');

        } else if (state === 'accepted') {
            follow_button.textContent = 'Follow';
            follow_button.dataset.state = 'none';
            follow_button.classList.remove('following');
            manageAuthorFollow(follow_button, user_uuid, author_uuid, 'DELETE');
        }
    });
}