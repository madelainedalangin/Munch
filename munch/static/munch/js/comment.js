"use strict"

const csrftoken = document.cookie.split('; ')
  .find(row => row.startsWith('csrftoken='))
  ?.split('=')[1];

document.addEventListener('DOMContentLoaded', () => {
  console.log('comment.js loaded');

  document.querySelectorAll('.comment-like-btn').forEach(button => {
    console.log('found button:', button);
    button.addEventListener('click', async () => {
      console.log('like button clicked!');
      const comment_fqid = button.dataset.commentFqid;
      const user_serial = button.dataset.userSerial;
      const icon = button.querySelector('.comment-like-icon');
      const count_span = button.closest('.comment-like').querySelector('.comment-like-count');
      // console.log('count_span:', count_span);
      // console.log('count_span text:', count_span?.textContent);
      // console.log('parsed:', parseInt(count_span?.textContent));
      const is_liked = button.dataset.liked === 'true';

      if (!is_liked) {
        const response = await fetch(`/munch/api/authors/${user_serial}/liked/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify({ object: comment_fqid })
        });

        if (response.ok) {
          button.dataset.liked = 'true';
          icon.src = icon.src.replace('like_no_fill.png', 'like_fill.png');
          count_span.textContent = (parseInt(count_span.textContent) || 0) + 1;
        }
      } else {
        const response = await fetch(`/munch/api/authors/${user_serial}/liked/`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
          },
          body: JSON.stringify({ object: comment_fqid })
        });

        if (response.ok) {
          button.dataset.liked = 'false';
          icon.src = icon.src.replace('like_fill.png', 'like_no_fill.png');
          count_span.textContent = (parseInt(count_span.textContent) || 0) - 1;
        }
      }
    });
  });
});