import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';
import Peer from 'simple-peer';
import styled from 'styled-components';

const Video = styled.video`
    border: 1px solid #ddd;
    margin: 5px;
    width: 250px;
`;

const VideoContainer = styled.div`
    display: flex;
    flex-wrap: wrap;
`;

const PeerVideo = ({ peer }) => {
    const ref = useRef();

    useEffect(() => {
        peer.on("stream", stream => {
            ref.current.srcObject = stream;
        });
    }, [peer]);

    return (
        <Video playsInline autoPlay ref={ref} />
    );
};


const VideoCall = ({ roomId }) => {
    const [peers, setPeers] = useState([]);
    const socketRef = useRef();
    const userVideo = useRef();
    const peersRef = useRef([]);

    useEffect(() => {
        socketRef.current = io.connect("http://localhost:8000", { path: "/socket.io" });
        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            userVideo.current.srcObject = stream;

            socketRef.current.emit("join", { roomId });

            socketRef.current.on("user-joined", payload => {
                const { sid, members } = payload;
                members.forEach(memberSid => {
                    const peer = createPeer(memberSid, socketRef.current.id, stream);
                    peersRef.current.push({
                        peerID: memberSid,
                        peer,
                    });
                    setPeers(peers => [...peers, { peerID: memberSid, peer }]);
                })
            });

            socketRef.current.on("offer", payload => {
                const { sid, signal, callerSid } = payload;
                const peer = addPeer(signal, callerSid, stream);
                peersRef.current.push({
                    peerID: callerSid,
                    peer,
                });

                setPeers(users => [...users, { peerID: callerSid, peer }]);
            });

            socketRef.current.on("answer", payload => {
                const { sid, signal } = payload;
                const item = peersRef.current.find(p => p.peerID === sid);
                item.peer.signal(signal);
            });

            socketRef.current.on("ice-candidate", payload => {
                const { sid, candidate } = payload;
                const item = peersRef.current.find(p => p.peerID === sid);
                item.peer.signal({ type: 'candidate', candidate });
            });

            socketRef.current.on("user-left", ({ sid }) => {
                const peerObj = peersRef.current.find(p => p.peerID === sid);
                if (peerObj) {
                    peerObj.peer.destroy();
                }
                const newPeers = peersRef.current.filter(p => p.peerID !== sid);
                peersRef.current = newPeers;
                setPeers(newPeers);
            });
        });

        return () => {
            socketRef.current.disconnect();
            peersRef.current.forEach(p => p.peer.destroy());
        };
    }, [roomId]);

    function createPeer(userToSignal, callerID, stream) {
        const peer = new Peer({
            initiator: true,
            trickle: false,
            stream,
        });

        peer.on("signal", signal => {
            socketRef.current.emit("offer", { targetSid: userToSignal, callerSid: callerID, signal });
        });

        return peer;
    }

    function addPeer(incomingSignal, callerID, stream) {
        const peer = new Peer({
            initiator: false,
            trickle: false,
            stream,
        });

        peer.on("signal", signal => {
            socketRef.current.emit("answer", { targetSid: callerID, callerSid: socketRef.current.id, signal });
        });

        peer.signal(incomingSignal);
        return peer;
    }

    return (
        <VideoContainer>
            <Video muted ref={userVideo} autoPlay playsInline />
            {peers.map((p) => (
                <PeerVideo key={p.peerID} peer={p.peer} />
            ))}
        </VideoContainer>
    );
};

export default VideoCall;
