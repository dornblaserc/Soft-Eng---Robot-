<?php
require_once __DIR__ . '/../includes/bootstrap.php';
$pageTitle = 'About - Etown Robotic Delivery Systems';
include 'Classes/header.php';

// Edit this list: name, role, bio, and photo filename (in website/images/team/)
$team = [
    [
        'name'  => 'Brandon Short',
        'role'  => 'Computer Engineer',
        'bio'   => 'I am a third-year engineering student enrolled at Elizabethtown College, exploring the exciting realms of problem-solving and innovation. 
                    Currently focused on Computer Engineering, 
                    I am enthusiastic about translating my classroom knowledge into real-world solutions.',
        'photo' => 'brandon_headshot.png',
        'linkedin' => 'https://www.linkedin.com/in/brandon-short-b17short20bluejaycrusader/'
    ],
    [
        'name'  => 'Chris Mensah',
        'role'  => 'Computer Engineer',
        'bio'   => 'Aspiring embedded systems developer with experience in C and microcontroller-based projects.
                    Focused on real-time systems and low-level programming.',
        'photo' => 'Chris_headshot.jpg',
        'linkedin' => 'https://www.linkedin.com/in/chrismensaha/'
    ],

    
    [
        'name'  => 'Chase Dornblaser',
        'role'  => 'Computer Engineer',
        'bio'   => 'As a Computer Engineering student at Elizabethtown College, 
                    I am passionate about using my skills in systems programming and machine learning to build innovative solutions.',
        'photo' => 'Chase_headshot.jpg',
        'linkedin' => 'https://www.linkedin.com/in/chase-dornblaser/'
    ],
    [
        'name'  => 'Noah Peiffer',
        'role'  => 'Computer Engineer',
        'bio'   => 'I am an undergraduate at Elizabethtown College, starting to look for roles in the computer engineering industry. As a computer engineering major, 
                    I am fascinated with electronics both on the hardware and software side. 
                    Being able to create electronic devices with my knowledge of electronics as well as coding motivates me to learn all I can about the field.',
        'photo' => 'Noah_headshot.jpg',
        'linkedin' => 'https://www.linkedin.com/in/noah-peiffer-computer-engineering/'
    ],
];

$photoDir = 'headshots/';
?>

<link rel="stylesheet" href="Styles/order.css?v=1">
<link rel="stylesheet" href="Styles/about.css?v=1">

<div class="page">

    <h2 class="page-title">About Us</h2>
    <p class="about-intro">
        We are the team behind Etown Robotic Delivery Systems, a robot that
        receives orders from this website and delivers them automatically.
    </p>

    <div class="team-grid">
        <?php foreach ($team as $member): ?>
            <article class="team-card">
                <?php if (file_exists(__DIR__ . '/' . $photoDir . $member['photo'])): ?>
                    <img class="team-photo"
                         src="<?= htmlspecialchars($photoDir . $member['photo']) ?>"
                         alt="Headshot of <?= htmlspecialchars($member['name']) ?>">
                <?php else: ?>
                    <div class="team-initial">
                        <?= htmlspecialchars(mb_strtoupper(mb_substr($member['name'], 0, 1))) ?>
                    </div>
                <?php endif; ?>

                <h3 class="team-name"><?= htmlspecialchars($member['name']) ?></h3>
                <p class="team-role"><?= htmlspecialchars($member['role']) ?></p>
                <p class="team-bio"><?= htmlspecialchars($member['bio']) ?></p>
                <a class="linkedin" href="<?= htmlspecialchars($member['linkedin']) ?>"><?= htmlspecialchars($member['name']) ?>'s Profile</a>
            </article>
        <?php endforeach; ?>
    </div>

</div>

<?php include 'Classes/footer.php'; ?>