function loadScript({url, params = {}}) {
    return new Promise(function (resolve, reject) {
        const script = document.createElement('script');
        url = url + parametrize(params)

        script.onload = () => resolve(script);
        script.onerror = () => reject(new Error(`Ошибка при загрузке ${url}`))
        script.src = url;

        document.head.appendChild(script);
    })
}

function parametrize(params) {
    let first = true;
    let result = '';

    for (let param in params) {
        if (first) {
            first = false;
            result += `?${param}=${params[param]}`
        } else {
            result += `&${param}=${params[param]}`
        }
    }

    return result
}

function range(start, end) {
    return new Proxy(
        {start, end},
        {
            has(target, prop) {
                return prop >= target.start && prop < target.end
            }
        });
}

function onlyUniqueValues(iterable) {
    return iterable.length === new Set(iterable).size;
}
