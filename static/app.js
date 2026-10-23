const list = document.querySelector('#bookmarks');
const message = document.querySelector('#message');
let selectedTag = '';

async function api(url, options = {}) {
    const response = await fetch(url, options);
    if (response.status === 204) return null;
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Не удалось выполнить запрос');
    return data;
}

async function loadBookmarks() {
    const bookmarks = await api('/api/bookmarks?tag=' + encodeURIComponent(selectedTag));
    list.replaceChildren();
    if (!bookmarks.length) list.textContent = 'Ничего не найдено.';
    for (const bookmark of bookmarks) {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = bookmark.url;
        link.textContent = bookmark.title;
        const tag = document.createElement('p');
        tag.textContent = bookmark.tag || 'Без тега';
        const remove = document.createElement('button');
        remove.textContent = 'Удалить';
        remove.addEventListener('click', async () => {
            try {
                await api('/api/bookmarks/' + bookmark.id, {method: 'DELETE'});
                await loadBookmarks();
            } catch (error) { message.textContent = error.message; }
        });
        item.append(link, tag, remove);
        list.append(item);
    }
}

document.querySelector('#add').addEventListener('submit', async (event) => {
    event.preventDefault();
    message.textContent = '';
    try {
        await api('/api/bookmarks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(Object.fromEntries(new FormData(event.target)))
        });
        event.target.reset();
        await loadBookmarks();
    } catch (error) { message.textContent = error.message; }
});
document.querySelector('#filter').addEventListener('submit', (event) => {
    event.preventDefault();
    selectedTag = new FormData(event.target).get('tag').trim().toLowerCase();
    loadBookmarks().catch(error => { message.textContent = error.message; });
});
loadBookmarks().catch(error => { message.textContent = error.message; });
