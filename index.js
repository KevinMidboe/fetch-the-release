require('dotenv').config()
const fetch = require('node-fetch')
const { whoAmI, printAll, writeCache, readCache } = require('./utils')

const BASE_URL = process.env.BASE_URL

const mapResult = (result) => {
  return {
    title: result.title,
    year: result.year,
    id: result.id,
    status: result.status,
    type: result.type,
    date: result.date
  }
}

const undownloaded = (media) => {
  return media.filter(item => item.status === 'requested')
}

function fetchRequestMedia() {
  return fetch(`${BASE_URL}/v2/request?page=1`)
    .then(resp => resp.json())
    .then(result => {
      const { results, total_results } = {...result}

      const media = results.map(mapResult)
      // console.log('requested: ', media)
      return media
    })
}

function fetchReleases(media) {
  const url = encodeURI(`${BASE_URL}/v1/pirate/search?query=${media.title}`)
  return fetch(url, {
      headers: { 
        'Authorization': process.env.AUTHORIZATION 
      }
    })
    .then(resp => resp.json())
//    .then(resp => { writeToFile(resp); return resp })
    .then(result => {
      const { results } = { ...result }
      console.log(`Releases for ${media.title} returned: ${results.length}`)
      return results ? {media: media, release: results } : null 
    })
    .catch(console.error)

}

function seasonedReleases(release) {
  const { media, releases } = release
  console.log(media.title)
  if (releases)
    console.log(releases[0])
  console.log()

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

  fetchRequestMedia()
    .then(media => Promise.all(media.map(fetchReleases)))
    .then(async(releases) => releases.map(await writeCache))
//  readCache()
//    .then(releases => releases.filter(seasonedReleases))
}


main()
