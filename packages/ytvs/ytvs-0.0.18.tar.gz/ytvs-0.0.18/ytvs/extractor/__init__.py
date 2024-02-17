import re

import requests
import json

from ytvs.utils import try_get, str_to_int, _search_regex, extract_view_count, extract_like_count, \
    convert_relative_to_absolute_date, _search_attribute, select_first_item_in_list, number_str_abbr_to_int, \
    is_korean_number, _search_attributes


class YoutubeBasicInfoExtractor:
    @staticmethod
    def _extract_channel_renderer(renderer):
        channel_id = try_get(renderer, lambda x: x['channelId'], str)
        type_name = 'channel'
        title = try_get(renderer, lambda x: x['title']['simpleText'], str)
        thumbnail = try_get(renderer, lambda x: x['thumbnail'], str)
        return {
            "id": channel_id,
            "type": type_name,
            "title": title,
            "thumbnail": thumbnail,
        }

    @staticmethod
    def extract_playlist_renderer(renderer):
        playlist_id = try_get(renderer, lambda x: x['channelId'], str)
        type_name = 'channel'
        thumbnails = try_get(renderer, lambda x: x['thumbnails'], str)
        title = try_get(renderer, lambda x: x["title"]["simpleText"], str)
        length = try_get(renderer, lambda x: x['videoCount'], str)
        videos = try_get(renderer, lambda x: x['videos'], str)
        video_count = try_get(renderer, lambda x: x['videoCount'], str)
        is_live = False
        return {
            "id": playlist_id,
            "type": type_name,
            "thumbnail": thumbnails,
            "title": title,
            "length": length,
            "videos": videos,
            "videoCount": video_count,
            "isLive": is_live
        }

    @staticmethod
    def _check_if_is_live_video(renderer):
        badges = try_get(renderer, lambda x: x['badges'])
        badge_metadata_renderer = _search_attribute(badges, 'metadataBadgeRenderer')
        badge_style = try_get(badge_metadata_renderer, lambda x: x['style'], str)
        if badge_style == "BADGE_STYLE_TYPE_LIVE_NOW":
            return True

        thumbnail_overlay = try_get(renderer, lambda x: x['thumbnailOverlays'])
        thumbnail_overlay_time_status_renderers = _search_attributes(thumbnail_overlay,
                                                                     'thumbnailOverlayTimeStatusRenderer') or []
        for thumbnail_overlay_time_status_renderer in thumbnail_overlay_time_status_renderers:
            style = try_get(thumbnail_overlay_time_status_renderer, "style")
            if style == 'LIVE':
                return True

        return False

    @staticmethod
    def extract_video_renderer(renderer):
        video_id = try_get(renderer, lambda x: x['videoId'], str)
        thumbnails = try_get(renderer, lambda x: x['thumbnail']['thumbnails'], list)
        thumbnail_urls = {}
        for idx, thumbnail in enumerate(thumbnails):

            if idx == 0:
                thumbnail_urls['default'] = thumbnail
            elif idx == 1:
                thumbnail_urls['medium'] = thumbnail
            elif idx == 2:
                thumbnail_urls['high'] = thumbnail

        owner_text_renderer = try_get(renderer, lambda x: x['ownerText'], dict)
        browse_endpoint_raw = _search_attribute(owner_text_renderer, 'browseEndpoint', max_depth=5)
        browse_endpoint = YoutubeBasicInfoExtractor.extract_browse_endpoint(browse_endpoint_raw)
        channel_handle = browse_endpoint['channel_url']
        channel_id = browse_endpoint['channel_id']

        title_runs = try_get(renderer, lambda x: x['title']['runs'], list)
        titles = []
        for title_run in title_runs:
            title_text = title_run['text']
            titles.append(title_text)
        title = "".join(titles)

        description_runs = try_get(renderer, lambda x: x['detailedMetadataSnippets'][0]['snippetText']['runs'],
                                   list) or []
        descriptions = []
        for description_run in description_runs:
            description_text = description_run['text']
            descriptions.append(description_text)
        description = "\r\n".join(descriptions)

        published_time_text = try_get(renderer, lambda x: x['publishedTimeText']['simpleText'], str)
        if not published_time_text is None:
            published_at = convert_relative_to_absolute_date(published_time_text)
        else:
            published_at = None

        duration_text = try_get(renderer, lambda x: x['lengthText']['simpleText'])

        channel_title_runs = try_get(renderer, lambda x: x['ownerText']['runs'], list)
        channel_titles = []
        for channel_title_run in channel_title_runs:
            channel_title = channel_title_run['text']
            channel_titles.append(channel_title)
        channel_title = "".join(channel_titles)
        is_live = YoutubeBasicInfoExtractor._check_if_is_live_video(renderer)

        return {
            'id': {
                'channelId': channel_id,
                'kind': 'youtube#video',
                'playlistId': None,
                'videoId': video_id
            },
            'etag': None,
            'kind': 'youtube#searchResult',
            'snippet': {
                "title": title,
                'channelId': channel_id,
                'channelTitle': channel_title,
                'description': description,
                "duration": duration_text,
                'liveBroadcastContent': is_live,
                'publishedAt': published_at,
                'thumbnails': thumbnail_urls,
            }
        }

    @staticmethod
    def _extract_browse_endpoint(renderer):
        channel_id = try_get(renderer, lambda x: x['browseId'], str)
        channel_handle = try_get(renderer, lambda x: x['canonicalBaseUrl'], str)
        return {
            'channel_id': channel_id,
            'channel_handle': channel_handle
        }

    @staticmethod
    def extract_metadata(metadata):
        title = try_get(metadata, lambda x: x['title'], str)
        description = try_get(metadata, lambda x: x['description'], str)
        rss_url = try_get(metadata, lambda x: x['rssUrl'], str)
        channel_conversion_url = try_get(metadata, lambda x: x['channelConversionUrl'], str)
        keywords = try_get(metadata, lambda x: x['keywords'], list)
        avatar_urls = try_get(metadata, lambda x: x['avatar']['thumbnails'], list)
        channel_url = try_get(metadata, lambda x: x['channelUrl'], list)
        is_family_safe = try_get(metadata, lambda x: x['isFamilySafe'], str)
        available_country_codes = try_get(metadata, lambda x: x['availableCountryCodes'], str)
        vanity_channel_url = try_get(metadata, lambda x: x['vanityChannelUrl'], str)

        return {
            'title': title,
            'description': description,
            'rss_url': rss_url,
            'channel_conversion_url': channel_conversion_url,
            'keywords': keywords,
            'avatar_urls': avatar_urls,
            'channel_url': channel_url,
            'is_family_safe': is_family_safe,
            'available_country_codes': available_country_codes,
            'vanity_channel_url': vanity_channel_url
        }

    @staticmethod
    def extract_channel_topbar(topbar):
        country_code = try_get(topbar, lambda x: x['countryCode'], str)
        return {"country_code": country_code}

    @staticmethod
    def _extract_thumbnail_renderer(renderer):
        if renderer is None:
            return None
        thumbnail_urls = {}
        for idx, banner_url in enumerate(renderer):
            if idx == 0:
                thumbnail_urls['default'] = banner_url
            elif idx == 1:
                thumbnail_urls['medium'] = banner_url
            elif idx == 2:
                thumbnail_urls['high'] = banner_url
        return thumbnail_urls

    @staticmethod
    def extract_channel_header(header):
        channel_id = try_get(header, lambda x: x['channelId'], str)
        title = try_get(header, lambda x: x['title'], str)
        avatars_renderer = try_get(header, lambda x: x['avatar']['thumbnails'], list)
        avatar_urls = YoutubeBasicInfoExtractor._extract_thumbnail_renderer(avatars_renderer)
        banners_renderer = try_get(header, lambda x: x['banner']['thumbnails'], list)
        banner_urls = YoutubeBasicInfoExtractor._extract_thumbnail_renderer(banners_renderer)

        tv_banners_renderer = try_get(header, lambda x: x['tvBanner']['thumbnails'], list)
        tv_banner_urls = YoutubeBasicInfoExtractor._extract_thumbnail_renderer(tv_banners_renderer)
        mobile_banners_renderer = try_get(header, lambda x: x['mobileBanner']['thumbnails'], list)
        mobile_banner_urls = YoutubeBasicInfoExtractor._extract_thumbnail_renderer(mobile_banners_renderer)
        channel_handle_text = try_get(header, lambda x: x['channelHandleText']['runs'][0]['text'])
        video_count_text = try_get(header, lambda x: x['videosCountText']['runs'][1]['text'])
        video_count = str_to_int(video_count_text)
        subscriber_count_text = try_get(header, lambda x: x['subscriberCountText']['simpleText'], str)
        if is_korean_number(subscriber_count_text):
            subscriber_count = number_str_abbr_to_int(subscriber_count_text)
        else:
            subscriber_count = str_to_int(subscriber_count_text)

        return {
            'channel_id': channel_id,
            'title': title,
            'avatar_urls': avatar_urls,
            'banner_urls': banner_urls,
            'tv_banner_urls': tv_banner_urls,
            'mobile_banner_urls': mobile_banner_urls,
            'channel_handle_text': channel_handle_text,
            'video_count': video_count,
            'subscriber_count': subscriber_count
        }

    @staticmethod
    def _extract_transcript_segment_renderer(renderer):
        target_id = try_get(renderer, lambda x: x['targetId'], str)
        start_ms = try_get(renderer, lambda x: x['startMs'], str)
        end_ms = try_get(renderer, lambda x: x['endMs'], str)
        tracking_params = try_get(renderer, lambda x: x['trackingParams'], str)
        text_runs = try_get(renderer, lambda x: x['snippet']['runs'], list)
        texts = []
        for text_run in text_runs:
            texts.append(text_run['text'])
        text = "".join(texts)

        return {
            'target_id': target_id,
            'start_ms': start_ms,
            'end_ms': end_ms,
            'text': text,
            'tracking_params': tracking_params
        }

    @staticmethod
    def _extract_transcript_section_header_renderer(renderer):
        start_ms = try_get(renderer, lambda x: x['startMs'], str)
        end_ms = try_get(renderer, lambda x: x['endMs'], str)
        title = try_get(renderer, lambda x: x['accessibility']['accessibilityData']['label'], str)
        tracking_params = try_get(renderer, lambda x: x['trackingParams'], str)

        return {
            "start_ms": start_ms,
            "end_ms": end_ms,
            "title": title,
            "tracking_params": tracking_params
        }

    @staticmethod
    def extract_transcript_segment_list_renderer(renderer):
        initial_segments = try_get(renderer, lambda x: x['initialSegments'])
        transcripts = []
        for initial_segment in initial_segments:
            for keyname in initial_segment.keys():
                if keyname == "transcriptSectionHeaderRenderer":
                    transcript = YoutubeBasicInfoExtractor._extract_transcript_section_header_renderer(initial_segment[keyname])
                    transcripts.append(transcript)
                elif keyname == 'transcriptSegmentRenderer':
                    transcript = YoutubeBasicInfoExtractor._extract_transcript_segment_renderer(initial_segment[keyname])
                    transcripts.append(transcript)

        return transcripts

    @staticmethod
    def extract_content_text(renderer):
        content_text_raws = try_get(renderer, lambda x: x['contentText']['runs'], list)
        content_texts = []
        for content_text_raw in content_text_raws:
            content_texts.append(content_text_raw['text'])
        content_text = "".join(content_texts)
        return content_text


    @staticmethod
    def extract_watch_endpoint(renderer):
        video_id = try_get(renderer, lambda x: x['videoId'], str)
        params = try_get(renderer, lambda x: x['params'], str)

        return {
            'videoId': video_id,
            'params': params
        }

    @staticmethod
    def _extract_web_command_metadata(renderer):
        send_post = try_get(renderer, lambda x: x['sendPost'], str)
        api_url = try_get(renderer, lambda x: x['apiUrl'], str)

        return {
            'sendPost': send_post,
            'apiUrl': api_url
        }

    @staticmethod
    def extract_continuation_command(renderer):
        token = try_get(renderer, lambda x: x['token'], str)
        request = try_get(renderer, lambda x: x['request'], str)

        return {
            'token': token,
            'request': request
        }

    @staticmethod
    def extract_continuation_item_renderer(renderer):
        click_tracking_params = try_get(renderer, lambda x: x['clickTrackingParams'], str)
        command_metadata_raw = try_get(renderer, lambda x: x['commandMetadata'], dict)
        web_command_metadata_raw = try_get(command_metadata_raw, lambda x: x['web_command_metadata'], dict)
        web_command_metadata = YoutubeBasicInfoExtractor._extract_web_command_metadata(web_command_metadata_raw)
        continuation_command_raw = try_get(renderer, lambda x: x['continuationCommand'], dict)
        continuation_comamnd = YoutubeBasicInfoExtractor.extract_continuation_command(continuation_command_raw)

        return {
            'click_tracking_params': click_tracking_params,
            'web_command_metadata': web_command_metadata,
            'continuation_command': continuation_comamnd,
        }

    @staticmethod
    def extract_comments_headerer_renderer(renderer):
        title = try_get(renderer, lambda x: x['titleText']['runs'][0]['text'], str)
        count = try_get(renderer, lambda x: x['commentsCount']['runs'][0]['text'], str)

        return {
            'title': title,
            'count': count
        }

    @staticmethod
    def _extract_button_renderer(renderer):
        text_runs = try_get(renderer, lambda x: x['text']['runs'], list)
        texts = []
        for text_run in text_runs:
            text = text_run['text']
            texts.append(text)
        text = "".join(texts)
        style = try_get(renderer, lambda x: x['style'], str)

        return {
            'text': text,
            'style': style
        }

    @staticmethod
    def extract_toggle_button_renderer(renderer):
        title = try_get(renderer, lambda x: x['defaultTooltip'], str)
        accessibility_label = try_get(renderer, lambda x: x['accessibilityData']['accessibilityData']['label'], str)
        count = extract_like_count(accessibility_label)
        return {
            'title': title,
            'accessibility_label': accessibility_label,
            'count': count
        }

    @staticmethod
    def extract_comment_replies_renderer(renderer):
        continuation_endpoint = try_get(renderer,
                                        lambda x: x['contents'][0]['continuationItemRenderer'][
                                            'continuationEndpoint'], dict)
        comment_replies_continuation = YoutubeBasicInfoExtractor.extract_continuation_item_renderer(continuation_endpoint)
        continuation_token = try_get(comment_replies_continuation, lambda x: x['continuation_command']['token'], str)
        return {
            'nextPageToken': continuation_token,
        }

    @staticmethod
    def extract_comment_renderer(renderer):
        author_text = try_get(renderer, (lambda x: x['authorText']['runs'][0]['text'],
                                         lambda x: x['authorText']['simpleText']), str)
        thumbnails = try_get(renderer, lambda x: x['authorThumbnail']['thumbnails'], list)
        thumbnail = select_first_item_in_list(thumbnails)



        browse_endpoint_raw = try_get(renderer, lambda x: x['authorEndpoint']['browseEndpoint'], dict)
        browse_endpoint = YoutubeBasicInfoExtractor.extract_browse_endpoint(browse_endpoint_raw)
        author_channel_url = browse_endpoint['channel_url']
        author_channel_id = browse_endpoint['channel_id']

        content_text = YoutubeBasicInfoExtractor.extract_content_text(renderer)
        # content_texts = []
        # for content_text_raw in content_text_raws:
        #     content_texts.append(content_text_raw['text'])
        # content_text = "".join(content_texts)

        comment_id = try_get(renderer, lambda x: x['commentId'], str)
        published_time_text = try_get(renderer, lambda x: x['publishedTimeText']['runs'][0]['text'], str)
        published_at = convert_relative_to_absolute_date(published_time_text)

        #
        action_buttons = try_get(renderer, lambda x: x['actionButtons']['commentActionButtonsRenderer'], dict)
        like_button = _search_attribute(action_buttons, 'likeButton')
        like_button_info = YoutubeBasicInfoExtractor.extract_toggle_button_renderer(like_button['toggleButtonRenderer'])

        watch_endpoint_renderer = try_get(renderer,
                                          lambda x: x['publishedTimeText']['runs'][0]['navigationEndpoint'][
                                              'watchEndpoint'], dict)
        watch_endpoint = YoutubeBasicInfoExtractor.extract_watch_endpoint(watch_endpoint_renderer)
        video_id = watch_endpoint['videoId']

        # reply_button = _search_attribute(action_buttons, 'replyButton')
        # reply_button_info = _extract_button_renderer(reply_button)

        return {  # root
            'etag': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
            'id': comment_id,
            'kind': 'youtube#commentThread',
            'replies': None,
            # snippet
            'snippet': {
                'canReply': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                'channelId': browse_endpoint['channel_id'],  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                'isPublic': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                # TopLevelComment
                'topLevelComment': {
                    'etag': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    'id': comment_id,
                    'kind': 'youtube#comment',
                    'snippet': {
                        'authorChannelUrl': author_channel_url,
                        'authorDisplayName': author_text,
                        'authorProfileImageUrl': thumbnail,
                        'canRate': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                        'channelId': author_channel_id,
                        'videoId':video_id,
                        'likeCount': like_button_info.get('count'),
                        'moderationStatus': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                        'parentId': '',
                        'publishedAt': published_at,
                        'textDisplay': content_text,
                        'textOriginal': content_text,
                        'updatedAt': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                        'viewerRating': 'none',  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    },
                    'totalReplyCount': 0,
                    'videoId': id,

                }
            }
        }



    @staticmethod
    def extract_comment_thread_renderer(renderer):
        author_text = try_get(renderer, (lambda x: x['authorText']['runs'][0]['text'],
                                         lambda x: x['authorText']['simpleText']), str)
        thumbnails = try_get(renderer, lambda x: x['authorThumbnail']['thumbnails'], list)
        thumbnail = select_first_item_in_list(thumbnails)



        browse_endpoint_raw = try_get(renderer, lambda x: x['authorEndpoint']['browseEndpoint'], dict)
        browse_endpoint = YoutubeBasicInfoExtractor.extract_browse_endpoint(browse_endpoint_raw)
        author_channel_url = browse_endpoint['channel_url']
        author_channel_id = browse_endpoint['channel_id']

        content_text = YoutubeBasicInfoExtractor.extract_content_text(renderer)
        # content_texts = []
        # for content_text_raw in content_text_raws:
        #     content_texts.append(content_text_raw['text'])
        # content_text = "".join(content_texts)

        comment_id = try_get(renderer, lambda x: x['commentId'], str)
        published_time_text = try_get(renderer, lambda x: x['publishedTimeText']['runs'][0]['text'], str)
        published_at = convert_relative_to_absolute_date(published_time_text)

        #
        action_buttons = try_get(renderer, lambda x: x['actionButtons']['commentActionButtonsRenderer'], dict)
        like_button = _search_attribute(action_buttons, 'likeButton')
        like_button_info = YoutubeBasicInfoExtractor.extract_toggle_button_renderer(like_button['toggleButtonRenderer'])

        watch_endpoint_renderer = try_get(renderer,
                                          lambda x: x['publishedTimeText']['runs'][0]['navigationEndpoint'][
                                              'watchEndpoint'], dict)
        watch_endpoint = YoutubeBasicInfoExtractor.extract_watch_endpoint(watch_endpoint_renderer)
        video_id = watch_endpoint['videoId']

        # reply_button = _search_attribute(action_buttons, 'replyButton')
        # reply_button_info = _extract_button_renderer(reply_button)

        return {  # root
            'etag': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
            'id': comment_id,
            'kind': 'youtube#commentThread',
            'replies': None,
            # snippet
            'snippet': {
                'canReply': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                'channelId': browse_endpoint['channel_id'],  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                'isPublic': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                # TopLevelComment
                'topLevelComment': {
                    'etag': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    'id': comment_id,
                    'kind': 'youtube#comment',
                    'snippet': {
                        'authorChannelUrl': author_channel_url,
                        'authorDisplayName': author_text,
                        'authorProfileImageUrl': thumbnail,
                        'canRate': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                        'channelId': author_channel_id,
                        'videoId':video_id,
                        'likeCount': like_button_info.get('count'),
                        'moderationStatus': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                        'parentId': '',
                        'publishedAt': published_at,
                        'textDisplay': content_text,
                        'textOriginal': content_text,
                        'updatedAt': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                        'viewerRating': 'none',  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    },
                    'totalReplyCount': 0,
                    'videoId': id,

                }
            }
        }



    @staticmethod
    def extract_comment_renderer(renderer):
        author_text = try_get(renderer, (lambda x: x['authorText']['runs'][0]['text'],
                                         lambda x: x['authorText']['simpleText']), str)
        thumbnails = try_get(renderer, lambda x: x['authorThumbnail']['thumbnails'], list)
        thumbnail = select_first_item_in_list(thumbnails)



        browse_endpoint_raw = try_get(renderer, lambda x: x['authorEndpoint']['browseEndpoint'], dict)
        browse_endpoint = YoutubeBasicInfoExtractor.extract_browse_endpoint(browse_endpoint_raw)
        author_channel_url = browse_endpoint['channel_url']
        author_channel_id = browse_endpoint['channel_id']

        content_text = YoutubeBasicInfoExtractor.extract_content_text(renderer)
        # content_texts = []
        # for content_text_raw in content_text_raws:
        #     content_texts.append(content_text_raw['text'])
        # content_text = "".join(content_texts)

        comment_id = try_get(renderer, lambda x: x['commentId'], str)
        published_time_text = try_get(renderer, lambda x: x['publishedTimeText']['runs'][0]['text'], str)
        published_at = convert_relative_to_absolute_date(published_time_text)

        #
        action_buttons = try_get(renderer, lambda x: x['actionButtons']['commentActionButtonsRenderer'], dict)
        like_button = _search_attribute(action_buttons, 'likeButton')
        like_button_info = YoutubeBasicInfoExtractor.extract_toggle_button_renderer(like_button['toggleButtonRenderer'])

        watch_endpoint_renderer = try_get(renderer,
                                          lambda x: x['publishedTimeText']['runs'][0]['navigationEndpoint'][
                                              'watchEndpoint'], dict)
        watch_endpoint = YoutubeBasicInfoExtractor.extract_watch_endpoint(watch_endpoint_renderer)
        video_id = watch_endpoint['videoId']

        # reply_button = _search_attribute(action_buttons, 'replyButton')
        # reply_button_info = _extract_button_renderer(reply_button)

        return {  # root

                'etag': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                'id': comment_id,
                'kind': 'youtube#comment',
                'snippet': {
                    'authorChannelUrl': author_channel_url,
                    'authorDisplayName': author_text,
                    'authorProfileImageUrl': thumbnail,
                    'canRate': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    'channelId': author_channel_id,
                    'videoId':video_id,
                    'likeCount': like_button_info.get('count'),
                    'moderationStatus': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    'parentId': '',
                    'publishedAt': published_at,
                    'textDisplay': content_text,
                    'textOriginal': content_text,
                    'updatedAt': None,  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                    'viewerRating': 'none',  # @TODO: 이정보가 필요하다면, 획득하는 방법에 대해 먼저 조사가 필요
                },
                'totalReplyCount': 0,
                'videoId': id,

            }

    @staticmethod
    def extract_browse_endpoint(renderer):
        channel_id = try_get(renderer, lambda x: x['browseId'], str)
        channel_url = try_get(renderer, lambda x: x['canonicalBaseUrl'], str)
        return {
            'channel_id': channel_id,
            'channel_url': channel_url
        }

    @staticmethod
    def extract_comments_header_renderer(renderer):
        if renderer is None:
            return None
        title_runs = try_get(renderer, lambda x: x['headerText']['runs'])
        titles = []
        for title_run in title_runs:
            titles.append(title_run['text'])
        title = "".join(titles)
        comment_count = try_get(renderer, lambda x: x['commentCount']['simpleText'])
        if comment_count is None:
            comment_count = "0"

        if is_korean_number(comment_count):
            comment_count = number_str_abbr_to_int(comment_count)
        else:
            comment_count = str_to_int(comment_count)
        return {
            'title': title,
            'comment_count': comment_count,
        }

    @staticmethod
    def extract_video_owner_renderer(renderer):
        title = try_get(renderer, lambda x: x['title']['runs'][0]['text'])
        channel_handle = try_get(renderer, lambda x: x['title']['runs'][0]['navigationEndpoint']['browseEndpoint'][
            'canonicalBaseUrl'])
        channel_id = try_get(renderer,
                             lambda x: x['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'])
        thumbnails = try_get(renderer, lambda x: x['thumbnail']['thumbnails'], dict)
        # TODO: 정규표현식을 이용해서 파싱해야됨
        subscribers = try_get(renderer, lambda x: x['subscriberCountText']['simpleText'], str)

        return {
            'title': title,
            'channel_handle': channel_handle,
            'channel_id': channel_id,
            "thumbnails": thumbnails,
            'subscribers': subscribers
        }

    @staticmethod
    def extract_video(renderer):
        # video_id = renderer['videoId']
        # 영상 제목 획득
        # titles = [try_get(renderer, lambda x: x['title']['runs'][0]['text'], str),
        #           try_get(renderer, lambda x: x['title']['runs'][1]['text'], str),
        #           try_get(renderer, lambda x: x['title']['runs'][2]['text'], str)]
        # title = "".join(filter(lambda x: x is not None, titles))
        title_runs = try_get(renderer, lambda x: x['title']['runs'], list)
        titles = []
        for title_run in title_runs:
            title_text = title_run['text']
            titles.append(title_text)
        title = "".join(titles)

        # 영상 설명 획득
        view_count_text = try_get(
            renderer, (lambda x: x['viewCount']['videoViewCountRenderer']['viewCount']['simpleText'],
                       lambda x: x['viewCount']['videoViewCountRenderer']['originalViewCount'], # Live streaming
                       ), str
        )
        # 해시태그 목록 획득
        super_title_links_raw = try_get(renderer, lambda x: x['superTitleLink']['runs']) or []
        super_title_links = []
        for super_title_link_raw in super_title_links_raw:
            title_link = super_title_link_raw['text']
            if title_link.strip() == "":
                continue
            super_title_links.append(title_link)

        # 조회수 횟수 획득
        view_count = extract_view_count(view_count_text)
        # view_count = str_to_int(_search_regex(r'^([\d,]+)', re.sub(r'\s', '', view_count_text), 'view count', default=None))

        # Like 횟수 획득
        menu_renderer = try_get(renderer, lambda x: x['videoActions']['menuRenderer'], dict)
        like_button_view_model = try_get(menu_renderer,
                                         lambda x: x['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel'][
                                             'likeButtonViewModel']['likeButtonViewModel']['toggleButtonViewModel'][
                                             'toggleButtonViewModel'][
                                             'defaultButtonViewModel'][
                                             'buttonViewModel'], dict)

        like_count_text = try_get(like_button_view_model, lambda x: x['accessibilityText'])
        like_count = extract_like_count(like_count_text)

        published_at = try_get(renderer, lambda x: x['dateText']['simpleText'])
        if  published_at is not None:
            published_at = convert_relative_to_absolute_date(published_at)
        else:
            published_at = None

        return {
            'title': title,
            'view_count': view_count,
            'like_count': like_count,
            'super_title_links': super_title_links,
            'published_at': published_at
        }

    @staticmethod
    def extract_yt_initial_data(html_text: str):
        yt_init_data = html_text.split("var ytInitialData =")
        if yt_init_data and len(yt_init_data) > 1:
            data = yt_init_data[1].split("</script>")[0].strip()[:-1]

            if "innertubeApiKey" in html_text:
                api_token = html_text.split("innertubeApiKey")[1].strip().split(",")[0].split('"')[2]
            else:
                api_token = None

            if "INNERTUBE_CONTEXT" in html_text:
                context = json.loads(html_text.split("INNERTUBE_CONTEXT")[1].strip()[2:-2])
            else:
                context = None

            init_data = json.loads(data)
            return {"init_data": init_data, "api_token": api_token, "context": context}
        else:
            print("cannot_get_init_data")
            return None

    @staticmethod
    def get_youtube_init_data(self, url):
        init_data = {}
        api_token = None
        context = None
        try:
            page = requests.get(url)
            yt_init_data = page.text.split("var ytInitialData =")
            if yt_init_data and len(yt_init_data) > 1:
                data = yt_init_data[1].split("</script>")[0].strip()[:-1]

                if "innertubeApiKey" in page.text:
                    api_token = page.text.split("innertubeApiKey")[1].strip().split(",")[0].split('"')[2]

                if "INNERTUBE_CONTEXT" in page.text:
                    context = json.loads(page.text.split("INNERTUBE_CONTEXT")[1].strip()[2:-2])

                init_data = json.loads(data)
                return {"init_data": init_data, "api_token": api_token, "context": context}
            else:
                print("cannot_get_init_data")
                return None
        except Exception as ex:
            print(ex)
