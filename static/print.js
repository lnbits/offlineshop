/* globals window, TextEncoder, NostrTools, LNbits */
window.PageOfflineshopPrint = {
  template: '#page-offlineshop-print',
  data() {
    return {
      items: []
    }
  },
  methods: {
    setBech32(url) {
      const bytes = new TextEncoder().encode(url)
      const bech32 = NostrTools.nip19.encodeBytes('lnurl', bytes)
      return `lightning:${bech32.toUpperCase()}`
    },
    loadItems() {
      const params = new URLSearchParams(window.location.search)
      return LNbits.api
        .request(
          'GET',
          `/offlineshop/api/v1/offlineshop/print?items=${params.get('items') || ''}`
        )
        .then(response => {
          this.items = response.data
          this.$nextTick(() => window.print())
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    }
  },
  created() {
    this.loadItems()
  }
}
