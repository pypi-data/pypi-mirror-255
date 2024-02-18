<%page/>

body {
    min-height: 100vh;
    color: #404040;
}

.navbar-img {
    max-width: 300px;
}

.btn {
    box-shadow: 0 0 4px rgba(0,0,0,.14), 0 4px 8px rgba(0,0,0,.28);
}

.splash {
    background: -webkit-radial-gradient(#41a3ff, #0273D4);
    background: radial-gradient(#41a3ff, #0273D4);
    color: #fff;
    text-align: center;
    box-shadow: inset 0 -16px 16px -16px rgba(0,0,0,0.28);
    padding: 70px 0 70px 0;
}

.splash h1 {
    font-weight: 500;
    text-shadow: 0px 1px 3px #0273D4
}

.description a {
    color: #0062cc;
}

.attunegif {
    box-shadow: 0 0 4px rgba(0,0,0,.14), 0 4px 8px rgba(0,0,0,.28);
    height:300px;
}

a {
    color: inherit;
}

a:hover {
    color: rgb(3, 27, 78);
    text-decoration: inherit;
}

.card {
    border-radius: 1rem;
}

.jumbotron {
    padding: 2em;
    background-color: rgba(200, 223, 255, 0.4);
    border-radius: 1rem;
}

.documentation {
    width: 100%;
    background-color: white;
}

.toc {
    z-index: 1000;
}

.tech-card {
    display: block;
    text-decoration: none;
    padding: 15px;
    border-radius: 2px;
    border: 1px solid #e9f0f3;
    text-align: left;
    -webkit-transition: 0.2s;
    transition: 0.2s;
    background: #fff;
}

.attune-ad {
    background-image: "https://www.servertribe.com/wp-content/uploads/2022/05/home_row_background_1-1.jpg";
    background-repeat: no-repeat;
    background-color: rgba(200, 223, 255, 0.4);
    background-size: cover;
    border-radius: 1rem;
}

.attune-ad h5 {
    color: rgb(0, 12, 43);
    font-size: 16px;
    font-weight: 700;
    line-height: 24px;
    margin: 0px 0px 8px;
}

.attune-ad p {
    color: rgb(77, 91, 124);
    font-size: 14px;
    line-height: 20px;
    margin: 0px;
}

.attune-ad a {
    font-size: .75rem;
}

code[class*="language-"] {
    font-size: 14px;
    margin-bottom: 1em;
}

:not(pre) > code[class*="language-"] {
    padding: .5em 1em !important;
    background: #081b4b;
}

pre[class*="language-"] {
    padding: 0 1em;
    margin-bottom: 1em;
    border-radius: 10px;
    white-space: normal !important;
    background: #081b4b;
}

.prompts {
    padding: .5em;
}