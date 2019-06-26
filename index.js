require('dotenv').config()
const fetch = require('node-fetch')
const { whoAmI, printAll } = require('./utils')

const BASE_PATH = process.env.BASE_PATH 

const mapResult = (result) => {
  return {
    title: result.title,
    year: result.year,
    id: result.id,
    status: result.status,
    date: result.date
  }
}

const undownloaded = (media) => {
  return media.filter(item => item.status === 'requested')
}

function fetchRequestMedia() {
  return fetch(`${BASE_PATH}/v2/request?page=1`)
    .then(resp => resp.json())
    .then(result => {
      const { results, total_results } = {...result}

      const media = results.map(mapResult)
      return media
    })
}

function fetchReleases(media) {
  const url = encodeURI(`${BASE_PATH}/v1/pirate/search?query=${media.title}`)
  return fetch(url, {
      headers: { 
        'Authorization': process.env.AUTHORIZATION 
      }
    })
    .then(resp => resp.json())
    .then(result => {
      const { results } = { ...result }
      console.log(`Releases for ${media.title} returned: ${results.length}`)
      return results ? {catch: media, release: results } : null 
    })
    .catch(console.error)

}

async function Fetch() {
  const media = await fetchRequestMedia()
  printAll(media)
  return media
}

async function Release(media) {
  Promise.all(media.map(fetchReleases))
    .then(releases => {
      // TODO could maybe return here ?
      // releases.forEach(r => console.log(`Release for ${r.media.title}:\n${r.results.length}`))
      Promise.resolve()
    })
}

function main() {
  console.info("👋🎣 lets do some fetch-and-releasin'\n")

  Fetch().then(Release)
}


main()
