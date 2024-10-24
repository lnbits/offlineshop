/* globals Quasar, Vue, _, VueQrcode, windowMixin, LNbits, LOCALE */
const pica = window.pica()

function imgSizeFit(img, maxWidth = 1024, maxHeight = 768) {
  let ratio = Math.min(
    1,
    maxWidth / img.naturalWidth,
    maxHeight / img.naturalHeight
  )
  return {width: img.naturalWidth * ratio, height: img.naturalHeight * ratio}
}

window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      selectedWallet: null,
      confirmationMethod: 'wordlist',
      wordlistTainted: false,
      offlineshop: {
        method: null,
        wordlist: [],
        items: []
      },
      itemDialog: {
        show: false,
        urlImg: true,
        data: {},
        units: []
      }
    }
  },
  computed: {
    printItems() {
      return this.offlineshop.items.filter(({enabled}) => enabled)
    }
  },
  watch: {
    selectedWallet() {
      this.loadShop()
    },
  },
  methods: {
    openNewDialog() {
      this.itemDialog.show = true
      this.itemDialog.data = {}
    },
    openUpdateDialog(itemId) {
      this.itemDialog.show = true
      let item = this.offlineshop.items.find(item => item.id === itemId)
      if (item.image.startsWith('data:')) {
        this.itemDialog.urlImg = false
      }
      this.itemDialog.data = item
    },
    imageAdded(file) {
      let blobURL = URL.createObjectURL(file)
      let image = new Image()
      image.src = blobURL
      image.onload = async () => {
        let fit = imgSizeFit(image, 100, 100)
        let canvas = document.createElement('canvas')
        canvas.setAttribute('width', fit.width)
        canvas.setAttribute('height', fit.height)
        output = await pica.resize(image, canvas)
        this.itemDialog.data.image = output.toDataURL('image/jpeg', 0.4)
        this.itemDialog = {...this.itemDialog}
      }
    },
    imageCleared() {
      this.itemDialog.data.image = null
      this.itemDialog = {...this.itemDialog}
    },
    disabledAddItemButton() {
      return (
        !this.itemDialog.data.name ||
        this.itemDialog.data.name.length === 0 ||
        !this.itemDialog.data.price ||
        !this.itemDialog.data.description ||
        !this.itemDialog.data.unit ||
        this.itemDialog.data.unit.length === 0
      )
    },
    loadShop() {
      LNbits.api
        .request(
          'GET',
          '/offlineshop/api/v1/offlineshop',
          this.selectedWallet.inkey
        )
        .then(response => {
          this.offlineshop = response.data
          this.confirmationMethod = response.data.method
          this.wordlistTainted = false
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    async setMethod() {
      try {
        await LNbits.api.request(
          'PUT',
          '/offlineshop/api/v1/offlineshop/method',
          this.selectedWallet.adminkey,
          {method: this.confirmationMethod, wordlist: this.offlineshop.wordlist}
        )
      } catch (err) {
        LNbits.utils.notifyApiError(err)
        return
      }

      this.$q.notify({
        message:
          `Method set to ${this.confirmationMethod}.` +
          (this.confirmationMethod === 'wordlist' ? ' Counter reset.' : ''),
        timeout: 700
      })
      this.loadShop()
    },
    async sendItem() {
      let {id, name, image, description, price, unit} = this.itemDialog.data
      const data = {
        name,
        description,
        image,
        price,
        unit
      }

      try {
        if (id) {
          await LNbits.api.request(
            'PUT',
            '/offlineshop/api/v1/offlineshop/items/' + id,
            this.selectedWallet.adminkey,
            data
          )
        } else {
          await LNbits.api.request(
            'POST',
            '/offlineshop/api/v1/offlineshop/items',
            this.selectedWallet.adminkey,
            data
          )
          this.$q.notify({
            message: `Item '${this.itemDialog.data.name}' added.`,
            timeout: 700
          })
        }
      } catch (err) {
        LNbits.utils.notifyApiError(err)
        return
      }

      this.loadShop()
      this.itemDialog.show = false
      this.itemDialog.urlImg = true
      this.itemDialog.data = {...defaultItemData}
    },
    toggleItem(itemId) {
      let item = this.offlineshop.items.find(item => item.id === itemId)
      item.enabled = !item.enabled

      LNbits.api
        .request(
          'PUT',
          '/offlineshop/api/v1/offlineshop/items/' + itemId,
          this.selectedWallet.adminkey,
          item
        )
        .then(() => {
          this.$q.notify({
            message: `Item ${item.enabled ? 'enabled' : 'disabled'}.`,
            timeout: 700
          })
          this.offlineshop.items = this.offlineshop.items
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    deleteItem(itemId) {
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this item?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/offlineshop/api/v1/offlineshop/items/' + itemId,
              this.selectedWallet.adminkey
            )
            .then(() => {
              this.$q.notify({
                message: `Item deleted.`,
                timeout: 700
              })
              this.offlineshop.items.splice(
                this.offlineshop.items.findIndex(item => item.id === itemId),
                1
              )
            })
            .catch(err => {
              LNbits.utils.notifyApiError(err)
            })
        })
    },
    itemPrice(price, unit) {
      return `${unit == 'sats' ? price : price.toFixed(2)} ${unit}`
    }
  },
  async created() {
    this.selectedWallet = this.g.user.wallets[0]
    this.loadShop()

    this.itemDialog.units = await LNbits.api.getCurrencies()
    console.log(this.itemDialog.units)
  }
})
