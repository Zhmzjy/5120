    async handleMapClick(lat, lng) {
      // Add search location marker first
      this.$refs.parkingMap.addSearchLocationMarker(lat, lng)

      // Then find nearby parking
      await this.handleFindParking(lat, lng)
    },

