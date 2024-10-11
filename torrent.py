import libtorrent as lt
import asyncio

class TorrentDownloader:
    def __init__(self, save_path='/home/abhishek/D/Torrent-to-Disk'):
        self.save_path = save_path
        self.download_active = True
        self.ses = lt.session()
        self.ses.listen_on(6881, 6891)  # Fallback for port configuration

    async def download_torrent(self, magnet_link):
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = self.save_path
        handle = self.ses.add_torrent(params)
        self.download_active = True

        # Wait for metadata asynchronously
        while not handle.status().has_metadata:
            await asyncio.sleep(1)

        # Get the torrent info
        torrent_info = handle.get_torrent_info()
        file_name = torrent_info.name()

        # Start the download loop
        async for progress, download_rate, upload_rate, num_peers, num_seeds, num_peers, downloaded_bytes, total_bytes in self.download_loop(handle):
            yield file_name, progress, download_rate, upload_rate, num_peers, num_seeds, num_peers, downloaded_bytes, total_bytes

    async def download_loop(self, handle):
        while self.download_active and handle.status().state != lt.torrent_status.seeding:
            status = handle.status()
            progress = status.progress * 100
            download_rate = status.download_rate / 1000  # kB/s
            upload_rate = status.upload_rate / 1000  # kB/s
            num_peers = status.num_peers
            num_seeds = status.num_seeds
            num_peers = status.num_peers
            downloaded_bytes = status.total_done
            total_bytes = status.total_wanted

            yield progress, download_rate, upload_rate, num_peers, num_seeds, num_peers, downloaded_bytes, total_bytes

            await asyncio.sleep(1)

    def stop_download(self):
        self.download_active = False