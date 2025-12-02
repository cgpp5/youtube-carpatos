#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for video filtering and sorting functionality
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from dateutil import parser as date_parser


class TestVideoFiltering(unittest.TestCase):
    """Test cases for get_new_videos function filtering and sorting"""

    def setUp(self):
        """Set up test fixtures"""
        self.today = datetime.now()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)

    def _create_mock_entry(self, video_id: str, title: str, published_dt: datetime):
        """Helper to create a mock RSS entry"""
        entry = MagicMock()
        entry.yt_videoid = video_id
        entry.title = title
        entry.link = f"https://youtube.com/watch?v={video_id}"
        entry.published = published_dt.isoformat()
        return entry

    @patch('src.youtube.feedparser')
    def test_filters_videos_to_current_date(self, mock_feedparser):
        """Test that only videos published today are returned"""
        from src.youtube import get_new_videos

        # Create entries: 1 from today, 1 from yesterday, 1 from tomorrow
        mock_feed = MagicMock()
        mock_feed.entries = [
            self._create_mock_entry("video1", "Today Video", self.today),
            self._create_mock_entry("video2", "Yesterday Video", self.yesterday),
            self._create_mock_entry("video3", "Tomorrow Video", self.tomorrow),
        ]
        mock_feedparser.parse.return_value = mock_feed

        result = get_new_videos(set())

        # Only today's video should be returned
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], "video1")
        self.assertEqual(result[0]['title'], "Today Video")

    @patch('src.youtube.feedparser')
    def test_sorts_videos_chronologically(self, mock_feedparser):
        """Test that multiple videos are sorted oldest first"""
        from src.youtube import get_new_videos

        # Create 3 videos from today with different times
        morning = self.today.replace(hour=9, minute=0, second=0, microsecond=0)
        noon = self.today.replace(hour=12, minute=0, second=0, microsecond=0)
        evening = self.today.replace(hour=18, minute=0, second=0, microsecond=0)

        mock_feed = MagicMock()
        # Add them in reverse order (newest first)
        mock_feed.entries = [
            self._create_mock_entry("video_evening", "Evening Video", evening),
            self._create_mock_entry("video_noon", "Noon Video", noon),
            self._create_mock_entry("video_morning", "Morning Video", morning),
        ]
        mock_feedparser.parse.return_value = mock_feed

        result = get_new_videos(set())

        # Should be sorted oldest first
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], "video_morning")
        self.assertEqual(result[1]['id'], "video_noon")
        self.assertEqual(result[2]['id'], "video_evening")

    @patch('src.youtube.feedparser')
    def test_excludes_already_processed_videos(self, mock_feedparser):
        """Test that already processed videos are excluded"""
        from src.youtube import get_new_videos

        mock_feed = MagicMock()
        mock_feed.entries = [
            self._create_mock_entry("video1", "New Video", self.today),
            self._create_mock_entry("video2", "Already Processed", self.today),
        ]
        mock_feedparser.parse.return_value = mock_feed

        result = get_new_videos({'video2'})

        # Only new video should be returned
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], "video1")

    @patch('src.youtube.feedparser')
    def test_returns_empty_list_when_no_videos_today(self, mock_feedparser):
        """Test that empty list is returned when no videos are from today"""
        from src.youtube import get_new_videos

        mock_feed = MagicMock()
        mock_feed.entries = [
            self._create_mock_entry("video1", "Old Video", self.yesterday),
        ]
        mock_feedparser.parse.return_value = mock_feed

        result = get_new_videos(set())

        self.assertEqual(result, [])

    @patch('src.youtube.feedparser')
    def test_returns_empty_list_when_no_entries(self, mock_feedparser):
        """Test that empty list is returned when RSS feed has no entries"""
        from src.youtube import get_new_videos

        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_feedparser.parse.return_value = mock_feed

        result = get_new_videos(set())

        self.assertEqual(result, [])

    @patch('src.youtube.feedparser')
    def test_video_dict_has_expected_keys(self, mock_feedparser):
        """Test that returned video dictionaries have the expected structure"""
        from src.youtube import get_new_videos

        mock_feed = MagicMock()
        mock_feed.entries = [
            self._create_mock_entry("video1", "Test Video", self.today),
        ]
        mock_feedparser.parse.return_value = mock_feed

        result = get_new_videos(set())

        self.assertEqual(len(result), 1)
        video = result[0]
        self.assertIn('id', video)
        self.assertIn('title', video)
        self.assertIn('link', video)
        self.assertIn('published', video)
        # Internal sorting key should be removed
        self.assertNotIn('_published_dt', video)


if __name__ == '__main__':
    unittest.main()
