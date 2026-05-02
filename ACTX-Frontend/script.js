const API_BASE_URL = "http://127.0.0.1:5000";
let searchHistory = JSON.parse(localStorage.getItem('actx_history') || '[]');
let worksData = [];

function renderHistory() {
    document.getElementById('history').innerHTML = searchHistory.map(name => `
        <span class="h-tag" onclick="autoSearch('${name}')">${name}</span>
    `).join('');
}

function autoSearch(name) {
    document.getElementById('actorInput').value = name;
    fetchData();
}

async function fetchData() {
    const query = document.getElementById('actorInput').value;
    const errorDisplay = document.getElementById('error-display');
    if (!query) return;

    errorDisplay.style.display = 'none';
    document.getElementById('result').style.display = 'none';
    document.getElementById('loader').style.display = 'block';

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); 

        const res = await fetch(`${API_BASE_URL}/api/search/universal?query=${encodeURIComponent(query)}`, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        const data = await res.json();
        
        if (data.person && !data.person.error) {
            renderPerson(data.person);
        } else if (data.movie && !data.movie.error) {
            renderMedia(data.movie, 'movie');
        } else if (data.tv && !data.tv.error) {
            renderMedia(data.tv, 'tv');
        } else {
            throw new Error("EMPTY_DATA");
        }

        document.getElementById('loader').style.display = 'none';
        document.getElementById('result').style.display = 'flex';

    } catch(e) { 
        document.getElementById('loader').style.display = 'none';
        errorDisplay.style.display = 'block';
        
        if (e.name === 'AbortError' || e.message.includes('Failed to fetch')) {
            errorDisplay.innerText = "🚨 Error: Server unreachable.";
        } else if (e.message === "EMPTY_DATA") {
            errorDisplay.innerText = "🔍 No records found.";
        } else {
            errorDisplay.innerText = "⚠️ Unexpected error.";
        }
    }
}

function renderPerson(data) {
    updateHistory(data.name);
    document.getElementById('p-img').src = data.image || 'https://via.placeholder.com/220x320/1e293b/94a3b8?text=No+Photo';
    document.getElementById('p-name').innerText = data.name;
    document.getElementById('p-bio').innerHTML = `Born: ${data.birthday}<br>Place: ${data.place}`;
    document.getElementById('section-title').innerText = "FILMOGRAPHY";
    
    document.getElementById('lbl-1').innerHTML = '<i class="fas fa-user-tag"></i> Character:';
    document.getElementById('lbl-3').innerHTML = '<i class="fas fa-video"></i> Director:';
    document.getElementById('lbl-4').innerHTML = '<i class="fas fa-hourglass-half"></i> Duration:';

    worksData = data.works;
    const worksContainer = document.getElementById('p-works');
    
    worksContainer.innerHTML = data.works.map((m, i) => {
        const initial = m.title ? m.title.charAt(0).toUpperCase() : '?';
        const fallbackSrc = `https://via.placeholder.com/105x155/1e293b/00d2ff?text=${initial}`;
        return `
        <div class="movie-item" onclick="showDetail(${i}, this)">
            <img class="movie-poster" 
                 src="${m.poster || fallbackSrc}" 
                 title="${m.title} - ${m.character}"
                 onerror="this.onerror=null; this.src='${fallbackSrc}';">
        </div>
        `;
    }).join('');

    document.getElementById('detailPanel').style.display = 'none';
    setupHorizontalScroll();
}

function renderMedia(data, type) {
    updateHistory(data.title);
    document.getElementById('p-img').src = data.poster || 'https://via.placeholder.com/220x320';
    document.getElementById('p-name').innerText = data.title;
    
    const releaseDateObj = new Date(data.release_date);
    const isReleased = data.status === "Released" || releaseDateObj <= new Date();
    const releaseLabel = isReleased ? "Released:" : "Expected:";
    
    document.getElementById('p-bio').innerHTML = `<b>${releaseLabel}</b> ${data.release_date || 'TBA'}<br>Genres: ${data.genres.join(', ')}`;
    document.getElementById('section-title').innerText = "OVERVIEW";
    document.getElementById('p-works').innerHTML = `<p class="overview-text">${data.overview.trim()}</p>`;
    
    const panel = document.getElementById('detailPanel');
    panel.style.display = 'block';
    document.getElementById('m-title').innerText = type === 'movie' ? "Movie Analytics" : "Series Analytics";
    
    document.getElementById('lbl-1').innerHTML = type === 'movie' ? 
        '<i class="fas fa-video"></i> Director:' : 
        '<i class="fas fa-users"></i> Creator:';

    document.getElementById('lbl-3').innerHTML = type === 'movie' ? 
        '<i class="fas fa-clock"></i> Runtime:' : 
        '<i class="fas fa-list-ol"></i> Episodes:';

    document.getElementById('lbl-4').innerHTML = type === 'movie' ? 
        '<i class="fas fa-money-bill-wave"></i> Budget:' : 
        '<i class="fas fa-layer-group"></i> Seasons:';

    document.getElementById('m-char').innerText = data.director || data.creator || 'N/A';
    document.getElementById('m-rel').innerText = data.status;
    document.getElementById('m-dir').innerText = type === 'movie' ? `${data.runtime} min` : data.episodes_count;

    if (type === 'movie') {
        document.getElementById('m-dur').innerText = data.budget > 0 
            ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(data.budget)
            : "Not Disclosed";
    } else {
        document.getElementById('m-dur').innerText = data.seasons_count;
    }

    document.getElementById('m-rate').innerText = data.rating;
    document.getElementById('m-writ').innerText = data.writer || "N/A";
}

function updateHistory(name) {
    if (!searchHistory.includes(name)) {
        searchHistory.unshift(name);
        searchHistory = searchHistory.slice(0, 3);
        localStorage.setItem('actx_history', JSON.stringify(searchHistory));
        renderHistory();
    }
}

async function showDetail(index, element) {
    document.querySelectorAll('.movie-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    const m = worksData[index];
    const panel = document.getElementById('detailPanel');
    const grid = document.getElementById('detailGrid');
    
    panel.style.display = 'block';
    grid.style.opacity = '0.3';
    
    document.getElementById('m-title').innerText = m.title;
    document.getElementById('m-char').innerText = m.character;
    
    const movieDateObj = new Date(m.release);
    const isReleased = m.release && movieDateObj <= new Date();
    document.getElementById('lbl-2').innerHTML = `<i class="fas fa-info-circle"></i> ${isReleased ? "Released:" : "Expected:"}`;
    document.getElementById('m-rel').innerText = m.release || 'TBA';

    try {
        const res = await fetch(`${API_BASE_URL}/api/movie/${m.id}`);
        const extra = await res.json();
        document.getElementById('m-dir').innerText = extra.director || 'N/A';
        document.getElementById('m-dur').innerText = `${extra.runtime || 0} min`;
        document.getElementById('m-rate').innerText = extra.rating || '0';
        document.getElementById('m-writ').innerText = extra.writer || 'N/A';
        grid.style.opacity = '1';
    } catch(e) { console.error("Metadata retrieval failed"); }
}

function setupHorizontalScroll() {
    const strip = document.querySelector('.movies-strip');
    if (!strip) return;
    strip.addEventListener('wheel', (e) => {
        if (e.deltaY !== 0) {
            e.preventDefault();
            strip.scrollLeft += e.deltaY; 
        }
    }, { passive: false });
}

document.getElementById('actorInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        fetchData();
    }
});

renderHistory();